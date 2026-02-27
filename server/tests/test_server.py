"""Tests for the denden server: servicer, response helpers, and gRPC integration."""
from __future__ import annotations

import threading
import time
from concurrent import futures

import grpc
import pytest

from denden.gen import denden_pb2, denden_pb2_grpc
from denden.server import (
    DENY_ROLE_NOT_ALLOWED,
    ERR_SUBAGENT_FAILURE,
    VERSION,
    DenDenServer,
    DendenServicer,
    denied_response,
    error_response,
    ok_response,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ask_request(request_id: str = "req-1") -> denden_pb2.DenDenRequest:
    return denden_pb2.DenDenRequest(
        denden_version=VERSION,
        request_id=request_id,
        ask_user=denden_pb2.AskUserPayload(question="pick a color"),
    )


def _delegate_request(request_id: str = "req-2") -> denden_pb2.DenDenRequest:
    return denden_pb2.DenDenRequest(
        denden_version=VERSION,
        request_id=request_id,
        delegate=denden_pb2.DelegatePayload(
            delegate_to=denden_pb2.IMPLEMENTER,
            task=denden_pb2.Task(text="do the thing"),
        ),
    )


def _echo_handler(request: denden_pb2.DenDenRequest) -> denden_pb2.DenDenResponse:
    """Handler that echoes the question or task text back."""
    if request.WhichOneof("payload") == "ask_user":
        return ok_response(
            request.request_id,
            ask_user_result=denden_pb2.AskUserResult(
                immediate=denden_pb2.ImmediateAnswer(text=request.ask_user.question),
            ),
        )
    return ok_response(
        request.request_id,
        delegate_result=denden_pb2.DelegateResult(
            delegation=denden_pb2.Delegation(
                summary=request.delegate.task.text,
                status=denden_pb2.DELEGATION_OK,
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Servicer unit tests (no gRPC transport)
# ---------------------------------------------------------------------------

class TestDendenServicer:
    def setup_method(self):
        self.servicer = DendenServicer()

    def test_missing_request_id(self):
        req = denden_pb2.DenDenRequest(
            ask_user=denden_pb2.AskUserPayload(question="hi"),
        )
        resp = self.servicer.Send(req, None)
        assert resp.status == denden_pb2.ERROR
        assert resp.error.code == "INVALID_REQUEST"
        assert "request_id" in resp.error.message

    def test_no_payload(self):
        req = denden_pb2.DenDenRequest(request_id="req-1")
        resp = self.servicer.Send(req, None)
        assert resp.status == denden_pb2.ERROR
        assert "payload" in resp.error.message

    def test_no_handler_registered(self):
        resp = self.servicer.Send(_ask_request(), None)
        assert resp.status == denden_pb2.ERROR
        assert "no handler registered" in resp.error.message

    def test_ask_user_dispatch(self):
        self.servicer.set_handler("ask_user", _echo_handler)
        resp = self.servicer.Send(_ask_request(), None)
        assert resp.status == denden_pb2.OK
        assert resp.ask_user_result.immediate.text == "pick a color"

    def test_delegate_dispatch(self):
        self.servicer.set_handler("delegate", _echo_handler)
        resp = self.servicer.Send(_delegate_request(), None)
        assert resp.status == denden_pb2.OK
        assert resp.delegate_result.delegation.summary == "do the thing"

    def test_handler_exception(self):
        def bad_handler(req):
            raise RuntimeError("boom")

        self.servicer.set_handler("ask_user", bad_handler)
        resp = self.servicer.Send(_ask_request(), None)
        assert resp.status == denden_pb2.ERROR
        assert resp.error.code == ERR_SUBAGENT_FAILURE
        assert "boom" in resp.error.message

    def test_status(self):
        resp = self.servicer.Status(denden_pb2.StatusRequest(), None)
        assert resp.uptime_seconds >= 0

    def test_only_registered_payload_dispatches(self):
        """Register ask_user only; delegate should fail."""
        self.servicer.set_handler("ask_user", _echo_handler)
        resp = self.servicer.Send(_delegate_request(), None)
        assert resp.status == denden_pb2.ERROR
        assert "no handler registered" in resp.error.message


# ---------------------------------------------------------------------------
# Response helper tests
# ---------------------------------------------------------------------------

class TestResponseHelpers:
    def test_ok_response_ask_user(self):
        result = denden_pb2.AskUserResult(
            immediate=denden_pb2.ImmediateAnswer(text="blue"),
        )
        resp = ok_response("req-1", ask_user_result=result)
        assert resp.status == denden_pb2.OK
        assert resp.request_id == "req-1"
        assert resp.denden_version == VERSION
        assert resp.ask_user_result.immediate.text == "blue"

    def test_ok_response_delegate(self):
        result = denden_pb2.DelegateResult(
            delegation=denden_pb2.Delegation(
                summary="done",
                status=denden_pb2.DELEGATION_OK,
            ),
        )
        resp = ok_response("req-2", delegate_result=result)
        assert resp.status == denden_pb2.OK
        assert resp.delegate_result.delegation.summary == "done"

    def test_ok_response_with_meta(self):
        meta = denden_pb2.ResponseMeta(orchestrator_action_id="act-1")
        resp = ok_response("req-1", meta=meta)
        assert resp.meta.orchestrator_action_id == "act-1"

    def test_denied_response(self):
        resp = denied_response("req-1", DENY_ROLE_NOT_ALLOWED, "nope")
        assert resp.status == denden_pb2.DENIED
        assert resp.error.code == DENY_ROLE_NOT_ALLOWED
        assert resp.error.message == "nope"
        assert resp.error.retryable is False

    def test_error_response(self):
        resp = error_response("req-1", "SOME_ERR", "failed", retryable=True)
        assert resp.status == denden_pb2.ERROR
        assert resp.error.code == "SOME_ERR"
        assert resp.error.retryable is True

    def test_error_response_default_not_retryable(self):
        resp = error_response("req-1", "ERR", "bad")
        assert resp.error.retryable is False


# ---------------------------------------------------------------------------
# DenDenServer handler registration
# ---------------------------------------------------------------------------

class TestDenDenServer:
    def test_on_ask_user_registers(self):
        server = DenDenServer()
        server.on_ask_user(_echo_handler)
        assert "ask_user" in server._servicer._handlers

    def test_on_delegate_registers(self):
        server = DenDenServer()
        server.on_delegate(_echo_handler)
        assert "delegate" in server._servicer._handlers


# ---------------------------------------------------------------------------
# gRPC integration tests (real transport)
# ---------------------------------------------------------------------------

@pytest.fixture()
def grpc_server():
    """Start a real gRPC server with echo handlers, yield a channel, then stop."""
    servicer = DendenServicer()
    servicer.set_handler("ask_user", _echo_handler)
    servicer.set_handler("delegate", _echo_handler)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    denden_pb2_grpc.add_DendenServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()

    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    yield channel

    channel.close()
    server.stop(grace=0)


class TestGRPCIntegration:
    def test_send_ask_user(self, grpc_server):
        stub = denden_pb2_grpc.DendenStub(grpc_server)
        resp = stub.Send(_ask_request())
        assert resp.status == denden_pb2.OK
        assert resp.ask_user_result.immediate.text == "pick a color"

    def test_send_delegate(self, grpc_server):
        stub = denden_pb2_grpc.DendenStub(grpc_server)
        resp = stub.Send(_delegate_request())
        assert resp.status == denden_pb2.OK
        assert resp.delegate_result.delegation.summary == "do the thing"
        assert resp.delegate_result.delegation.status == denden_pb2.DELEGATION_OK

    def test_send_no_payload(self, grpc_server):
        stub = denden_pb2_grpc.DendenStub(grpc_server)
        req = denden_pb2.DenDenRequest(request_id="req-x")
        resp = stub.Send(req)
        assert resp.status == denden_pb2.ERROR

    def test_status(self, grpc_server):
        stub = denden_pb2_grpc.DendenStub(grpc_server)
        resp = stub.Status(denden_pb2.StatusRequest())
        assert resp.uptime_seconds >= 0
