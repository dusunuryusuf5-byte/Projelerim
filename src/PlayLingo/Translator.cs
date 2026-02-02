using System;
using System.Collections.Generic;

namespace PlayLingo;

public class Translator
{
    private readonly Dictionary<string, Dictionary<string, string>> _translations;

    public Translator()
    {
        _translations = new()
        {
            ["en->tr"] = new()
            {
                ["hello"] = "merhaba",
                ["goodbye"] = "güle güle",
                ["thank you"] = "teşekkürler",
                ["yes"] = "evet",
                ["no"] = "hayır",
            },
            ["tr->en"] = new()
            {
                ["merhaba"] = "hello",
                ["güle güle"] = "goodbye",
                ["teşekkürler"] = "thank you",
                ["evet"] = "yes",
                ["hayır"] = "no",
            }
        };
    }

    public string Translate(string text, string src, string dest)
    {
        if (string.Equals(src, dest, StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Source and destination must differ", nameof(dest));

        var key = $"{src.ToLowerInvariant()}->{dest.ToLowerInvariant()}";
        if (!_translations.ContainsKey(key))
            throw new ArgumentException($"Unsupported language pair: {src}->{dest}");

        var phrase = (text ?? string.Empty).Trim().ToLowerInvariant();
        if (_translations[key].TryGetValue(phrase, out var translated))
            return translated;

        // If not found, return original text unchanged
        return text;
    }
}
