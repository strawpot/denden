from __future__ import annotations

import logging
import signal
import time
from concurrent import futures
from typing import Callable

import grpc

from denden.gen import denden_pb2, denden_pb2_grpc

logger = logging.getLogger(__name__)

# Denial / error code constants (available for orchestrators to use)
DENY_ROLE_NOT_ALLOWED = "DENY_ROLE_NOT_ALLOWED"
DENY_DEPTH_LIMIT = "DENY_DEPTH_LIMIT"
DENY_BUDGET_EXCEEDED = "DENY_BUDGET_EXCEEDED"
DENY_TOOLS_NOT_ALLOWED = "DENY_TOOLS_NOT_ALLOWED"
DENY_POLICY_REQUIRES_HUMAN = "DENY_POLICY_REQUIRES_HUMAN"
ERR_SUBAGENT_TIMEOUT = "ERR_SUBAGENT_TIMEOUT"
ERR_SUBAGENT_FAILURE = "ERR_SUBAGENT_FAILURE"

VERSION = "1.0"

# Type alias for request handlers.
# A handler receives a DenDenRequest and returns a DenDenResponse.
RequestHandler = Callable[[denden_pb2.DenDenRequest], denden_pb2.DenDenResponse]


class DendenServicer(denden_pb2_grpc.DendenServicer):
    """gRPC servicer that validates envelopes and dispatches to registered handlers."""

    def __init__(self) -> None:
        self._start_time = time.monotonic()
        self._handlers: dict[str, RequestHandler] = {}

    def set_handler(self, payload_key: str, handler: RequestHandler) -> None:
        """Register a handler for a payload type ('ask_user' or 'delegate')."""
        self._handlers[payload_key] = handler

    def Send(self, request: denden_pb2.DenDenRequest, context) -> denden_pb2.DenDenResponse:
        """Validate envelope and dispatch to the registered handler."""
        if not request.request_id:
            return _error_response(
                "", "INVALID_REQUEST", "request_id is required", retryable=False
            )
        if request.HasField("trace"):
            trace = request.trace
            if not trace.worktree_id and not trace.agent_instance_id:
                logger.warning("request %s missing trace fields", request.request_id)

        payload_type = request.WhichOneof("payload")
        if payload_type is None:
            return _error_response(
                request.request_id,
                "INVALID_REQUEST",
                "either 'ask_user' or 'delegate' payload is required",
                retryable=False,
            )

        handler = self._handlers.get(payload_type)
        if handler is None:
            return _error_response(
                request.request_id,
                "INVALID_REQUEST",
                f"no handler registered for payload type: {payload_type}",
                retryable=False,
            )

        try:
            return handler(request)
        except Exception as e:
            logger.exception("handler failed for request %s", request.request_id)
            return _error_response(
                request.request_id,
                ERR_SUBAGENT_FAILURE,
                str(e),
                retryable=False,
            )

    def Status(self, request, context) -> denden_pb2.StatusResponse:
        uptime = int(time.monotonic() - self._start_time)
        return denden_pb2.StatusResponse(
            uptime_seconds=uptime,
        )


# ---------------------------------------------------------------------------
# Response helpers (public, for use by orchestrators)
# ---------------------------------------------------------------------------

def ok_response(
    request_id: str,
    *,
    ask_user_result: denden_pb2.AskUserResult | None = None,
    delegate_result: denden_pb2.DelegateResult | None = None,
    meta: denden_pb2.ResponseMeta | None = None,
) -> denden_pb2.DenDenResponse:
    kwargs: dict = {
        "denden_version": VERSION,
        "request_id": request_id,
        "status": denden_pb2.OK,
    }
    if ask_user_result is not None:
        kwargs["ask_user_result"] = ask_user_result
    if delegate_result is not None:
        kwargs["delegate_result"] = delegate_result
    if meta is not None:
        kwargs["meta"] = meta
    return denden_pb2.DenDenResponse(**kwargs)


def denied_response(
    request_id: str, code: str, message: str,
    meta: denden_pb2.ResponseMeta | None = None,
) -> denden_pb2.DenDenResponse:
    kwargs: dict = {
        "denden_version": VERSION,
        "request_id": request_id,
        "status": denden_pb2.DENIED,
        "error": denden_pb2.ErrorDetail(code=code, message=message, retryable=False),
    }
    if meta is not None:
        kwargs["meta"] = meta
    return denden_pb2.DenDenResponse(**kwargs)


def _error_response(
    request_id: str, code: str, message: str, retryable: bool,
) -> denden_pb2.DenDenResponse:
    return denden_pb2.DenDenResponse(
        denden_version=VERSION,
        request_id=request_id,
        status=denden_pb2.ERROR,
        error=denden_pb2.ErrorDetail(
            code=code, message=message, retryable=retryable
        ),
    )


def error_response(
    request_id: str, code: str, message: str, retryable: bool = False,
    meta: denden_pb2.ResponseMeta | None = None,
) -> denden_pb2.DenDenResponse:
    kwargs: dict = {
        "denden_version": VERSION,
        "request_id": request_id,
        "status": denden_pb2.ERROR,
        "error": denden_pb2.ErrorDetail(
            code=code, message=message, retryable=retryable
        ),
    }
    if meta is not None:
        kwargs["meta"] = meta
    return denden_pb2.DenDenResponse(**kwargs)


class DenDenServer:
    """gRPC transport server for the DenDen protocol.

    Usage:
        server = DenDenServer(addr="127.0.0.1:9700")
        server.on_ask_user(my_ask_handler)
        server.on_delegate(my_delegate_handler)
        server.run()
    """

    def __init__(
        self,
        addr: str = "127.0.0.1:9700",
        max_workers: int = 10,
    ) -> None:
        self.addr = addr
        self.max_workers = max_workers
        self._servicer = DendenServicer()
        self._server: grpc.Server | None = None

    def on_ask_user(self, handler: RequestHandler) -> None:
        """Register a handler for ask_user requests."""
        self._servicer.set_handler("ask_user", handler)

    def on_delegate(self, handler: RequestHandler) -> None:
        """Register a handler for delegate requests."""
        self._servicer.set_handler("delegate", handler)

    def run(self) -> None:
        """Start the gRPC server and block until interrupted."""
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )
        denden_pb2_grpc.add_DendenServicer_to_server(self._servicer, self._server)
        self._server.add_insecure_port(self.addr)

        self._server.start()
        logger.info("denden server listening on %s", self.addr)

        def _shutdown(signum, frame):
            logger.info("shutting down...")
            self._server.stop(grace=5)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        self._server.wait_for_termination()
