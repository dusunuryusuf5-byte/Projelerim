import zipfile
from playlingo.diagnostics import collect_diagnostics_zip


def test_collect_diagnostics_zip(tmp_path):
    out = tmp_path / "out.zip"
    p = collect_diagnostics_zip(out_path=str(out))
    assert out.exists()
    with zipfile.ZipFile(str(out), "r") as z:
        namelist = z.namelist()
        assert "logs.txt" in namelist
        assert "sysinfo.txt" in namelist
