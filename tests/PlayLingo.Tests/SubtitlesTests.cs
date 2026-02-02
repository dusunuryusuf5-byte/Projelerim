using System;
using System.Collections.Generic;
using PlayLingo;
using Xunit;

public class SubtitlesTests
{
    [Fact]
    public void ParseAndComposeRoundtrip()
    {
        var srt = "1\n00:00:00,000 --> 00:00:01,000\nhello\n\n2\n00:00:01,000 --> 00:00:02,000\nthank you\n";
        var subs = Subtitles.ParseSrt(srt);
        var outSrt = Subtitles.ComposeSrt(subs);
        Assert.Contains("hello", outSrt);
        Assert.Contains("thank you", outSrt);
    }

    [Fact]
    public void TranslateDefaultField()
    {
        var subs = new List<Subtitle> { new Subtitle(1, TimeSpan.Zero, TimeSpan.FromSeconds(1), "hello"), new Subtitle(2, TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(2), "thank you") };
        var t = new Translator();
        var outSubs = Subtitles.TranslateSubtitles(subs, t, "en", "tr");
        Assert.Equal("merhaba", outSubs[0].Text);
        Assert.Equal("teşekkürler", outSubs[1].Text);
    }

    [Fact]
    public void TranslateCaptionField()
    {
        var subs = new List<Subtitle> { new Subtitle(1, TimeSpan.Zero, TimeSpan.FromSeconds(1), "ignored", "hello"), new Subtitle(2, TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(2), "ignored", "merhaba") };
        var t = new Translator();
        var outSubs = Subtitles.TranslateSubtitles(subs, t, "en", "tr", field: "caption");
        Assert.Equal("merhaba", outSubs[0].Caption);
        Assert.Equal("merhaba", outSubs[1].Caption);
    }

    [Fact]
    public void MissingCaptionThrowsWhenRequested()
    {
        var subs = new List<Subtitle> { new Subtitle(1, TimeSpan.Zero, TimeSpan.FromSeconds(1), "hello") };
        var t = new Translator();
        Assert.Throws<InvalidOperationException>(() => Subtitles.TranslateSubtitles(subs, t, "en", "tr", field: "caption"));
    }
}
