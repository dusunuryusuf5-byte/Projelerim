using System;
using PlayLingo;
using Xunit;

public class TranslatorTests
{
    [Fact]
    public void TranslateEnToTr()
    {
        var t = new Translator();
        Assert.Equal("merhaba", t.Translate("hello", "en", "tr"));
        Assert.Equal("teşekkürler", t.Translate("thank you", "en", "tr"));
    }

    [Fact]
    public void TranslateTrToEn()
    {
        var t = new Translator();
        Assert.Equal("hello", t.Translate("merhaba", "tr", "en"));
    }

    [Fact]
    public void UnknownPhraseReturnsOriginal()
    {
        var t = new Translator();
        var original = "unknown phrase";
        Assert.Equal(original, t.Translate(original, "en", "tr"));
    }

    [Fact]
    public void UnsupportedLanguageThrows()
    {
        var t = new Translator();
        Assert.Throws<ArgumentException>(() => t.Translate("hello", "en", "de"));
    }

    [Fact]
    public void SameLanguageThrows()
    {
        var t = new Translator();
        Assert.Throws<ArgumentException>(() => t.Translate("hello", "en", "en"));
    }
}
