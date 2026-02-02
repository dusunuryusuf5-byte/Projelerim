import os

from playlingo.diagnostics import send_report


def test_send_report_with_key(tmp_path, monkeypatch):
    out = tmp_path / "d.zip"
    open(out, "wb").write(b"dummy")

    called = {}

    def fake_post(url, files=None, headers=None, timeout=None):
        called['url'] = url
        called['headers'] = headers

        class R:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {'ok': True}

        return R()

    monkeypatch.setenv('DIAG_REPORT_API_KEY', 'secret123')
    monkeypatch.setattr('requests.post', fake_post)
    res = send_report('https://example.com/report', zip_path=str(out))
    assert res == {'ok': True}
    assert 'Authorization' in called['headers'] and called['headers']['Authorization'] == 'Bearer secret123'
