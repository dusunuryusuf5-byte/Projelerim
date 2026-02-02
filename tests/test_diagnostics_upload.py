import os
import json

from playlingo.diagnostics import send_report, create_github_issue_with_diagnostics, collect_diagnostics_zip


def test_send_report_monkeypatch(tmp_path, monkeypatch):
    # create a fake zip
    out = tmp_path / "d.zip"
    open(out, "wb").write(b"dummy")

    called = {}

    def fake_post(url, files=None, headers=None, timeout=None):
        called['url'] = url
        called['files'] = files
        called['headers'] = headers

        class R:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {'ok': True}

        return R()

    monkeypatch.setattr('requests.post', fake_post)
    res = send_report('https://example.com/report', zip_path=str(out))
    assert res == {'ok': True}
    assert 'Authorization' not in called['headers']


def test_create_github_issue_with_diagnostics_monkeypatch(tmp_path, monkeypatch):
    # create fake zip file
    out = collect_diagnostics_zip(out_path=str(tmp_path / 'd.zip'))

    gist_called = {}

    def fake_post(url, json=None, headers=None, timeout=None, files=None):
        if url.endswith('/gists'):
            gist_called['payload'] = json

            class R:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {'html_url': 'https://gist.github.com/foo'}

            return R()
        elif url.endswith('/issues'):
            gist_called['issue'] = json

            class R2:
                def raise_for_status(self):
                    pass

                def json(self):
                    return {'number': 123}

            return R2()
        raise RuntimeError('unexpected')

    monkeypatch.setenv('GITHUB_TOKEN', 'fake')
    monkeypatch.setattr('requests.post', fake_post)

    res = create_github_issue_with_diagnostics('me/repo', title='T', body='B')
    assert res == {'number': 123}
    assert 'Diagnostics gist' in gist_called['issue']['body']
