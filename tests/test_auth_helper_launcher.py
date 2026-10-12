"""Exercise generated launchers with a local, credential-free download server."""

import json
import os
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src import auth_helper


@pytest.mark.skipif(os.name != "nt", reason="Windows batch launcher")
@pytest.mark.parametrize("download_succeeds", [True, False])
def test_windows_launcher_downloads_next_to_itself_and_handles_partial_failure(
    tmp_path, download_succeeds
):
    if not shutil.which("curl"):
        pytest.skip("curl is not installed")
    requested = []
    helper_source = (
        "import json, sys\n"
        "print('LAUNCH_RESULT=' + json.dumps(sys.argv[1:]))\n"
    ).encode("utf-8")

    class DownloadHandler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            requested.append(self.path)
            self.send_response(200)
            self.send_header("Content-Length", str(len(helper_source)))
            self.end_headers()
            if download_succeeds:
                self.wfile.write(helper_source)
            else:
                # curl must fail for an incomplete response instead of leaving
                # a seemingly valid helper for the launcher to execute.
                self.wfile.write(helper_source[:10])
                self.close_connection = True

    server = ThreadingHTTPServer(("127.0.0.1", 0), DownloadHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        relay_url = f"http://127.0.0.1:{server.server_address[1]}"
        download_dir = tmp_path / "download folder"
        download_dir.mkdir()
        unrelated_dir = tmp_path / "unrelated"
        unrelated_dir.mkdir()
        launcher = download_dir / "start_auth.bat"
        launcher.write_bytes(
            auth_helper.render("bat", relay_url=relay_url, listener_port=9321).encode("utf-8")
        )
        result = subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(launcher)],
            cwd=unrelated_dir,
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        assert requested == ["/web/login/download?as=py"]
        assert not list(download_dir.glob("*.download*"))
        assert not (unrelated_dir / "web_login.py").exists()
        if download_succeeds:
            assert result.returncode == 0, result.stdout + result.stderr
            output = next(line for line in result.stdout.splitlines() if line.startswith("LAUNCH_RESULT="))
            assert json.loads(output.split("=", 1)[1]) == [
                "--relay", relay_url, "--port", "9321"
            ]
            assert (download_dir / "web_login.py").read_bytes() == helper_source
        else:
            assert result.returncode != 0
            assert "LAUNCH_RESULT=" not in result.stdout
            assert not (download_dir / "web_login.py").exists()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
