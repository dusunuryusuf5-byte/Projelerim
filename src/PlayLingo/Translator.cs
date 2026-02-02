using System;
using System.Collections.Generic;

namespace PlayLingo;

/// <summary>
/// Simple translator with a small, in-memory phrase dictionary.
/// </summary>
public class Translator
{
    private readonly Dictionary<string, Dictionary<string, string>> _translations;

    /// <summary>
    /// Initialize the built-in translation dictionary.
    /// </summary>
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

    /// <summary>
    /// Translate <paramref name="text"/> from <paramref name="src"/> to <paramref name="dest"/>.
    /// </summary>
    /// <exception cref="ArgumentException">Thrown when languages are unsupported or equal.</exception>
    public string Translate(string text, string src, string dest)
    {
        if (text is null) throw new ArgumentNullException(nameof(text));
        if (string.Equals(src, dest, StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException("Source and destination must differ", nameof(dest));

        var key = $"{src.ToLowerInvariant()}->{dest.ToLowerInvariant()}";
        if (!_translations.ContainsKey(key))
            throw new ArgumentException($"Unsupported language pair: {src}->{dest}");

        var phrase = (text ?? string.Empty).Trim().ToLowerInvariant();
        if (_translations[key].TryGetValue(phrase, out var translated))
            return translated!; // value is non-null by construction

        // If not found, return original text unchanged
        return text;
    }
}
