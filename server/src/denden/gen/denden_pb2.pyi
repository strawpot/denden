import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Format(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEXT: _ClassVar[Format]
    JSON: _ClassVar[Format]

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OK: _ClassVar[ResponseStatus]
    DENIED: _ClassVar[ResponseStatus]
    ERROR: _ClassVar[ResponseStatus]
TEXT: Format
JSON: Format
OK: ResponseStatus
DENIED: ResponseStatus
ERROR: ResponseStatus

class DenDenRequest(_message.Message):
    __slots__ = ("denden_version", "request_id", "trace", "ask_user", "delegate")
    DENDEN_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    TRACE_FIELD_NUMBER: _ClassVar[int]
    ASK_USER_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_FIELD_NUMBER: _ClassVar[int]
    denden_version: str
    request_id: str
    trace: Trace
    ask_user: AskUserPayload
    delegate: DelegatePayload
    def __init__(self, denden_version: _Optional[str] = ..., request_id: _Optional[str] = ..., trace: _Optional[_Union[Trace, _Mapping]] = ..., ask_user: _Optional[_Union[AskUserPayload, _Mapping]] = ..., delegate: _Optional[_Union[DelegatePayload, _Mapping]] = ...) -> None: ...

class Trace(_message.Message):
    __slots__ = ("run_id", "agent_instance_id", "parent_agent_instance_id", "created_at")
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    agent_instance_id: str
    parent_agent_instance_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, run_id: _Optional[str] = ..., agent_instance_id: _Optional[str] = ..., parent_agent_instance_id: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class AskUserPayload(_message.Message):
    __slots__ = ("question", "choices", "default_value", "why", "response_format")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    WHY_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    question: str
    choices: _containers.RepeatedScalarFieldContainer[str]
    default_value: str
    why: str
    response_format: Format
    def __init__(self, question: _Optional[str] = ..., choices: _Optional[_Iterable[str]] = ..., default_value: _Optional[str] = ..., why: _Optional[str] = ..., response_format: _Optional[_Union[Format, str]] = ...) -> None: ...

class DelegatePayload(_message.Message):
    __slots__ = ("delegate_to", "task")
    DELEGATE_TO_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    delegate_to: str
    task: Task
    def __init__(self, delegate_to: _Optional[str] = ..., task: _Optional[_Union[Task, _Mapping]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("text", "artifact_refs", "extra", "return_format")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_REFS_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    RETURN_FORMAT_FIELD_NUMBER: _ClassVar[int]
    text: str
    artifact_refs: _containers.RepeatedScalarFieldContainer[str]
    extra: _struct_pb2.Struct
    return_format: Format
    def __init__(self, text: _Optional[str] = ..., artifact_refs: _Optional[_Iterable[str]] = ..., extra: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., return_format: _Optional[_Union[Format, str]] = ...) -> None: ...

class DenDenResponse(_message.Message):
    __slots__ = ("denden_version", "request_id", "status", "error", "ask_user_result", "delegate_result")
    DENDEN_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ASK_USER_RESULT_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_RESULT_FIELD_NUMBER: _ClassVar[int]
    denden_version: str
    request_id: str
    status: ResponseStatus
    error: ErrorDetail
    ask_user_result: AskUserResult
    delegate_result: DelegateResult
    def __init__(self, denden_version: _Optional[str] = ..., request_id: _Optional[str] = ..., status: _Optional[_Union[ResponseStatus, str]] = ..., error: _Optional[_Union[ErrorDetail, _Mapping]] = ..., ask_user_result: _Optional[_Union[AskUserResult, _Mapping]] = ..., delegate_result: _Optional[_Union[DelegateResult, _Mapping]] = ...) -> None: ...

class ErrorDetail(_message.Message):
    __slots__ = ("code", "message", "retryable")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RETRYABLE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    retryable: bool
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., retryable: bool = ...) -> None: ...

class AskUserResult(_message.Message):
    __slots__ = ("text", "json")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    text: str
    json: _struct_pb2.Struct
    def __init__(self, text: _Optional[str] = ..., json: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DelegateResult(_message.Message):
    __slots__ = ("output_format", "output", "summary")
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    output_format: Format
    output: _struct_pb2.Struct
    summary: str
    def __init__(self, output_format: _Optional[_Union[Format, str]] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., summary: _Optional[str] = ...) -> None: ...

class StatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("uptime_seconds", "active_agents")
    UPTIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_AGENTS_FIELD_NUMBER: _ClassVar[int]
    uptime_seconds: int
    active_agents: int
    def __init__(self, uptime_seconds: _Optional[int] = ..., active_agents: _Optional[int] = ...) -> None: ...
