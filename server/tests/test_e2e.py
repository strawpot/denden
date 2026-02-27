"""End-to-end tests: Go CLI binary → Python gRPC server."""
from __future__ import annotations

import json
import os
import subprocess
import threading
import time
from concurrent import futures
from pathlib import Path

import grpc
import pytest

from denden.gen import denden_pb2, denden_pb2_grpc
from denden.server import (
    DENY_ROLE_NOT_ALLOWED,
    VERSION,
    DendenServicer,
    denied_response,
    ok_response,
)

ROOT = Path(__file__).resolve().parent.parent.parent
CLI_DIR = ROOT / "cli"
CLI_BIN = CLI_DIR / "denden"


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def _ask_handler(request: denden_pb2.DenDenRequest) -> denden_pb2.DenDenResponse:
    return ok_response(
        request.request_id,
        ask_user_result=denden_pb2.AskUserResult(text=request.ask_user.question),
    )


def _delegate_handler(request: denden_pb2.DenDenRequest) -> denden_pb2.DenDenResponse:
    task = request.delegate.task
    return ok_response(
        request.request_id,
        delegate_result=denden_pb2.DelegateResult(
            summary=task.text,
            output_format=task.return_format,
        ),
    )


def _deny_handler(request: denden_pb2.DenDenRequest) -> denden_pb2.DenDenResponse:
    return denied_response(
        request.request_id, DENY_ROLE_NOT_ALLOWED, "agents cannot delegate"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def cli_binary():
    """Build the Go CLI binary once for the test module."""
    if not CLI_DIR.exists():
        pytest.skip("cli/ directory not found")
    result = subprocess.run(
        ["go", "build", "-o", str(CLI_BIN), "."],
        cwd=str(CLI_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(f"go build failed:\n{result.stderr}")
    yield str(CLI_BIN)


@pytest.fixture(scope="module")
def server_addr():
    """Start a Python gRPC server with handlers, yield the address."""
    servicer = DendenServicer()
    servicer.set_handler("ask_user", _ask_handler)
    servicer.set_handler("delegate", _delegate_handler)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    denden_pb2_grpc.add_DendenServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()

    yield f"127.0.0.1:{port}"

    server.stop(grace=0)


@pytest.fixture(scope="module")
def deny_server_addr():
    """Start a server where delegate always returns DENIED."""
    servicer = DendenServicer()
    servicer.set_handler("ask_user", _ask_handler)
    servicer.set_handler("delegate", _deny_handler)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    denden_pb2_grpc.add_DendenServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()

    yield f"127.0.0.1:{port}"

    server.stop(grace=0)


def run_cli(binary: str, addr: str, *args: str, env_extra: dict | None = None):
    """Run the CLI binary and return (stdout, stderr, exit_code)."""
    env = os.environ.copy()
    env["DENDEN_ADDR"] = addr
    env["DENDEN_TIMEOUT"] = "5s"
    if env_extra:
        env.update(env_extra)

    result = subprocess.run(
        [binary, *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return result.stdout, result.stderr, result.returncode


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestE2EAskUser:
    def test_simple_question(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", '{"askUser":{"question":"what color?"}}',
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp.get("status", "OK") == "OK"
        assert resp["askUserResult"]["text"] == "what color?"

    def test_with_choices(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", '{"askUser":{"question":"pick one","choices":["a","b","c"]}}',
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp["askUserResult"]["text"] == "pick one"

    def test_auto_fills_request_id(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", '{"askUser":{"question":"hi"}}',
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp["requestId"].startswith("req_")

    def test_auto_fills_version(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", '{"askUser":{"question":"hi"}}',
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp["dendenVersion"] == VERSION


class TestE2EDelegate:
    def test_simple_delegate(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", json.dumps({
                "delegate": {
                    "delegateTo": "implementer",
                    "task": {"text": "build auth module", "returnFormat": "TEXT"},
                },
            }),
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp.get("status", "OK") == "OK"
        result = resp["delegateResult"]
        assert result["summary"] == "build auth module"

    def test_with_trace(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", json.dumps({
                "delegate": {
                    "delegateTo": "reviewer",
                    "task": {"text": "review PR"},
                },
                "trace": {
                    "runId": "run-123",
                    "agentInstanceId": "agent-abc",
                },
            }),
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp.get("status", "OK") == "OK"

    def test_with_env_trace(self, cli_binary, server_addr):
        """Trace fields from env vars should be used when not in JSON."""
        stdout, _, ec = run_cli(
            cli_binary, server_addr,
            "send", '{"delegate":{"delegateTo":"fixer","task":{"text":"fix bug"}}}',
            env_extra={
                "DENDEN_AGENT_ID": "env-agent-1",
                "DENDEN_PARENT_AGENT_ID": "env-parent-1",
                "DENDEN_RUN_ID": "env-run-1",
            },
        )
        assert ec == 0


class TestE2EDenied:
    def test_denied_response(self, cli_binary, deny_server_addr):
        stdout, _, ec = run_cli(
            cli_binary, deny_server_addr,
            "send", '{"delegate":{"delegateTo":"implementer","task":{"text":"x"}}}',
        )
        assert ec == 1
        resp = json.loads(stdout)
        assert resp["status"] == "DENIED"
        assert resp["error"]["code"] == DENY_ROLE_NOT_ALLOWED

    def test_ask_user_still_works_on_deny_server(self, cli_binary, deny_server_addr):
        """ask_user handler on the deny server should still work."""
        stdout, _, ec = run_cli(
            cli_binary, deny_server_addr,
            "send", '{"askUser":{"question":"hi"}}',
        )
        assert ec == 0
        resp = json.loads(stdout)
        assert resp.get("status", "OK") == "OK"


class TestE2EStatus:
    def test_status(self, cli_binary, server_addr):
        stdout, _, ec = run_cli(cli_binary, server_addr, "status")
        assert ec == 0
        resp = json.loads(stdout)
        assert "uptime_seconds" in resp
        assert "active_agents" in resp
        assert resp["uptime_seconds"] >= 0


class TestE2EErrors:
    def test_invalid_json(self, cli_binary, server_addr):
        _, stderr, ec = run_cli(cli_binary, server_addr, "send", "{bad}")
        assert ec == 1
        assert "invalid JSON" in stderr

    def test_no_payload(self, cli_binary, server_addr):
        _, stderr, ec = run_cli(cli_binary, server_addr, "send", "{}")
        assert ec == 1
        assert "payload" in stderr

    def test_unknown_command(self, cli_binary, server_addr):
        _, stderr, ec = run_cli(cli_binary, server_addr, "bogus")
        assert ec == 1
        assert "unknown command" in stderr

    def test_no_args(self, cli_binary, server_addr):
        _, stderr, ec = run_cli(cli_binary, server_addr)
        assert ec == 1
        assert "usage:" in stderr

    def test_connection_refused(self, cli_binary):
        """CLI should fail gracefully when server is not running."""
        _, stderr, ec = run_cli(cli_binary, "127.0.0.1:19999", "status")
        assert ec == 1
