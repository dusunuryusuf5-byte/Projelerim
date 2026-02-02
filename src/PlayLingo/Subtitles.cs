using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace PlayLingo;

public record Subtitle(int Index, TimeSpan Start, TimeSpan End, string Text, string? Caption = null);

public static class Subtitles
{
    public static List<Subtitle> ParseSrt(string srt)
    {
        var blocks = srt.Split(new[] { "\r\n\r\n", "\n\n" }, StringSplitOptions.RemoveEmptyEntries);
        var result = new List<Subtitle>();
        foreach (var block in blocks)
        {
            var lines = block.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None).Where(l => !string.IsNullOrWhiteSpace(l)).ToArray();
            if (lines.Length < 3) continue;
            if (!int.TryParse(lines[0].Trim(), out var index)) continue;
            var times = lines[1].Split("-->", StringSplitOptions.None);
            var start = ParseSrtTimestamp(times[0].Trim());
            var end = ParseSrtTimestamp(times[1].Trim());
            var content = string.Join("\n", lines.Skip(2));
            result.Add(new Subtitle(index, start, end, content));
        }
        return result;
    }

    public static string ComposeSrt(IEnumerable<Subtitle> subs)
    {
        var sb = new StringBuilder();
        var first = true;
        foreach (var s in subs)
        {
            if (!first) sb.AppendLine();
            first = false;
            sb.AppendLine(s.Index.ToString());
            sb.AppendLine($"{FormatSrtTimestamp(s.Start)} --> {FormatSrtTimestamp(s.End)}");
            sb.AppendLine(s.Text);
        }
        return sb.ToString();
    }

    public static List<Subtitle> TranslateSubtitles(IEnumerable<Subtitle> subtitles, Translator translator, string src, string dest, string field = "text")
    {
        if (translator is null) throw new ArgumentNullException(nameof(translator));
        // Validate language pair by a sample call
        _ = translator.Translate("__playlingo_sanity_check__", src, dest);

        var outList = new List<Subtitle>();
        foreach (var s in subtitles)
        {
            if (s is null) throw new ArgumentException("Subtitle cannot be null");
            var newText = s.Text;
            var newCaption = s.Caption;

            if (field.Equals("text", StringComparison.OrdinalIgnoreCase))
                newText = translator.Translate(s.Text, src, dest);
            else if (field.Equals("caption", StringComparison.OrdinalIgnoreCase))
            {
                if (s.Caption is null) throw new InvalidOperationException("Caption field missing on subtitle");
                newCaption = translator.Translate(s.Caption, src, dest);
            }
            else
            {
                throw new NotSupportedException($"Field '{field}' is not supported");
            }

            outList.Add(new Subtitle(s.Index, s.Start, s.End, newText, newCaption));
        }

        return outList;
    }

    private static TimeSpan ParseSrtTimestamp(string ts)
    {
        // ts like "00:00:01,000"
        var fixedTs = ts.Replace(',', '.');
        if (TimeSpan.TryParseExact(fixedTs, @"hh\:mm\:ss\.fff", CultureInfo.InvariantCulture, out var t))
            return t;
        return TimeSpan.Zero;
    }

    private static string FormatSrtTimestamp(TimeSpan ts)
    {
        // format as 00:00:01,000
        return ts.ToString(@"hh\:mm\:ss\,fff", CultureInfo.InvariantCulture);
    }
}
