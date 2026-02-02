"""Diagnostics collection helpers.

Provides:
- collect_diagnostics_zip(out_path=None, include_overlay_config=True) -> path to zip file
- install_crash_handler(root, report_callback=None) -> installs tkinter exception handler

The zip contains:
- logs.txt (from in-memory log handler if present)
- overlay_config.json (if exists)
- env.json (selected environment info)
- sysinfo.txt (platform and Python version)
- gitsha.txt (if git available)
"""
from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from typing import Optional

from .logging_config import get_memory_handler, dump_logs_to_file
from .gui import _CONFIG_PATH

logger = logging.getLogger(__name__)


def _get_git_sha() -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return None


def _write_pip_freeze(dest: Path):
    try:
        # Prefer importlib.metadata to list installed distributions
        try:
            from importlib import metadata
        except Exception:
            import importlib_metadata as metadata  # type: ignore

        lines = []
        for dist in metadata.distributions():
            name = getattr(dist, "metadata", None)
            try:
                # metadata.name may not be present; fallback to dist.metadata['Name']
                ver = dist.version
                nm = dist.metadata.get('Name') or getattr(dist, 'name', None) or ''
            except Exception:
                nm = getattr(dist, 'name', '')
                ver = getattr(dist, 'version', '')
            if nm:
                lines.append(f"{nm}=={ver}")
        if not lines:
            # fallback to pip freeze
            import subprocess

            out = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
            dest.write_text(out, encoding="utf-8")
            return
        dest.write_text("\n".join(sorted(lines)), encoding="utf-8")
    except Exception:
        try:
            import subprocess

            out = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
            dest.write_text(out, encoding="utf-8")
        except Exception:
            dest.write_text("pip freeze failed\n", encoding="utf-8")


def _write_psutil_info(dest: Path):
    try:
        import psutil

        info = {
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disk": {p.mountpoint: dict(psutil.disk_usage(p.mountpoint)._asdict()) for p in psutil.disk_partitions()},
        }
        dest.write_text(json.dumps(info, indent=2), encoding="utf-8")
    except Exception:
        dest.write_text("psutil not available or failed\n", encoding="utf-8")


def _write_screenshot(dest: Path):
    try:
        from PIL import ImageGrab

        img = ImageGrab.grab()
        img.save(str(dest))
    except Exception:
        dest.write_text("screenshot not available", encoding="utf-8")


def collect_diagnostics_zip(out_path: Optional[str] = None, include_overlay_config: bool = True, include_sysinfo_details: bool = True, include_screenshot: bool = False, include_pip_packages: bool = True) -> str:
    """Collect diagnostics and write to a zip file. Returns path to zip."""
    tmpdir = Path(tempfile.mkdtemp(prefix="playlingo_diag_"))
    try:
        # logs
        mh = get_memory_handler()
        logs_file = tmpdir / "logs.txt"
        if mh:
            dump_logs_to_file(str(logs_file))
        else:
            # fallback: capture root logger recent output
            logs_file.write_text("No in-memory logs available\n", encoding="utf-8")

        # overlay config
        if include_overlay_config and _CONFIG_PATH.exists():
            shutil.copy2(_CONFIG_PATH, tmpdir / "overlay_config.json")

        # env
        env = {k: v for k, v in os.environ.items() if k.startswith("PLAYLINGO_")}
        (tmpdir / "env.json").write_text(json.dumps(env, indent=2), encoding="utf-8")

        # sys info
        (tmpdir / "sysinfo.txt").write_text(f"Platform: {platform.platform()}\nPython: {platform.python_version()}\n", encoding="utf-8")

        if include_sysinfo_details:
            _write_psutil_info(tmpdir / "sysinfo_details.json")

        if include_pip_packages:
            _write_pip_freeze(tmpdir / "pip_freeze.txt")

        # screenshot
        if include_screenshot:
            _write_screenshot(tmpdir / "screenshot.png")

        # git sha
        sha = _get_git_sha()
        if sha:
            (tmpdir / "gitsha.txt").write_text(sha, encoding="utf-8")

        # create zip
        outp = Path(out_path) if out_path else Path(tempfile.gettempdir()) / f"playlingo_diag_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
        with ZipFile(outp, "w") as z:
            for p in sorted(tmpdir.iterdir()):
                z.write(p, arcname=p.name)
        return str(outp)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            logger.exception("Failed to cleanup tempdir %s", tmpdir)


def send_report(url: str, api_key_env: str = "DIAG_REPORT_API_KEY", zip_path: Optional[str] = None) -> dict:
    """Send diagnostics zip to given URL via POST multipart. Requires env var API key if needed.

    Returns parsed JSON response or raises.
    """
    import requests

    headers = {}
    key = os.environ.get(api_key_env)
    if key:
        headers["Authorization"] = f"Bearer {key}"

    if zip_path is None:
        zip_path = collect_diagnostics_zip()

    with open(zip_path, "rb") as fh:
        files = {"file": (os.path.basename(zip_path), fh, "application/zip")}
        r = requests.post(url, files=files, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()


def create_github_issue_with_diagnostics(repo: str, token_env: str = "GITHUB_TOKEN", title: str = "PlayLingo Diagnostics Report", body: Optional[str] = None) -> dict:
    """Create a GitHub issue in repo (owner/repo) and attach diagnostics via a gist link.

    Returns the issue JSON as dict. Requires token in env variable.
    """
    import base64
    import requests

    token = os.environ.get(token_env)
    if not token:
        raise RuntimeError("GITHUB_TOKEN not found in environment")

    zip_path = collect_diagnostics_zip()

    # Create a Gist with base64-encoded zip (since zip is binary)
    b64 = base64.b64encode(open(zip_path, "rb").read()).decode("ascii")
    gist_payload = {"files": {"diagnostics_base64.txt": {"content": b64}}, "public": False, "description": "PlayLingo diagnostics (base64 zip)"}
    gh_headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    r = requests.post("https://api.github.com/gists", json=gist_payload, headers=gh_headers, timeout=30)
    r.raise_for_status()
    gist = r.json()

    gist_url = gist.get("html_url") or gist.get("html_url")
    issue_body = (body or "") + f"\n\nDiagnostics gist: {gist_url}"
    issue_payload = {"title": title, "body": issue_body}
    owner, name = repo.split("/")
    r2 = requests.post(f"https://api.github.com/repos/{owner}/{name}/issues", json=issue_payload, headers=gh_headers, timeout=30)
    r2.raise_for_status()
    return r2.json()

def install_crash_handler(root, report_callback: Optional[callable] = None):
    """Install Tkinter exception hook to capture uncaught exceptions.

    report_callback(path_to_zip) will be called with the produced zip path when a dump occurs.
    """

    def _handler(exc, val, tb):
        try:
            logger.exception("Unhandled exception in GUI", exc_info=(exc, val, tb))
            zip_path = collect_diagnostics_zip()
            logger.info("Diagnostics collected to %s", zip_path)
            if report_callback:
                try:
                    report_callback(zip_path)
                except Exception:
                    logger.exception("report_callback failed")
        except Exception:
            logger.exception("Crash handler failed")

    # For tkinter, set report_callback_exception on the root
    try:
        root.report_callback_exception = lambda exc, val, tb: _handler(exc, val, tb)
    except Exception:
        # fallback to sys.excepthook
        import sys

        sys.excepthook = lambda exc, val, tb: _handler(exc, val, tb)
