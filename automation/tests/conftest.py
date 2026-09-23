from dataclasses import dataclass
from threading import Thread
import os

import pytest
from werkzeug.serving import WSGIRequestHandler, make_server

from automation.client import LabClient
from automation.lab.app import create_app


class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


@dataclass
class Lab:
    url: str
    database: str


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Optionally use an installed Chromium; default is Playwright's browser."""
    executable = os.getenv("QA_BROWSER_EXECUTABLE")
    if executable:
        return {**browser_type_launch_args, "executable_path": executable}
    return browser_type_launch_args


@pytest.fixture
def lab(tmp_path):
    database = tmp_path / "test.sqlite3"
    app = create_app(database)
    server = make_server("127.0.0.1", 0, app, threaded=True, request_handler=QuietHandler)
    thread = Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    yield Lab(f"http://127.0.0.1:{server.server_port}", str(database))
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


@pytest.fixture
def api(lab):
    client = LabClient(lab.url)
    yield client
    client.session.close()
