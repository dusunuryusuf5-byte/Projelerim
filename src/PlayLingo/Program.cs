using System;
using System.IO;
using System.Linq;

namespace PlayLingo;

/// <summary>
/// CLI entrypoint for the PlayLingo .NET tool.
/// </summary>
public static class Program
{
    /// <summary>
    /// Main entrypoint. Supported command: <c>translate-srt</c>.
    /// </summary>
    public static int Main(string[] args)
    {
        if (args is null || args.Length == 0)
        {
            Console.Error.WriteLine("Usage: playlingo translate-srt --input <in.srt> --output <out.srt> --src en --dest tr [--field text]");
            return 2;
        }

        // simple arg parsing
        if (args.Length >= 1 && args[0] == "translate-srt")
        {
            string? input = null;
            string? output = null;
            string? src = null;
            string? dest = null;
            string field = "text";

            for (int i = 1; i < args.Length; i++)
            {
                var a = args[i];
                if ((a == "--input" || a == "-i") && i + 1 < args.Length) input = args[++i];
                else if ((a == "--output" || a == "-o") && i + 1 < args.Length) output = args[++i];
                else if (a == "--src" && i + 1 < args.Length) src = args[++i];
                else if (a == "--dest" && i + 1 < args.Length) dest = args[++i];
                else if (a == "--field" && i + 1 < args.Length) field = args[++i];
            }

            if (input is null || output is null || src is null || dest is null)
            {
                Console.Error.WriteLine("Missing required args");
                return 2;
            }

            var text = File.ReadAllText(input);
            var subs = Subtitles.ParseSrt(text);
            var translator = new Translator();
            var translated = Subtitles.TranslateSubtitles(subs, translator, src, dest, field);
            var outText = Subtitles.ComposeSrt(translated);
            File.WriteAllText(output, outText);
            Console.WriteLine($"Wrote translated SRT to {output}");
            return 0;
        }

        Console.Error.WriteLine("Unknown command");
        return 2;
    }
}
