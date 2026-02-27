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

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNSPECIFIED: _ClassVar[Role]
    PLANNER: _ClassVar[Role]
    IMPLEMENTER: _ClassVar[Role]
    REVIEWER: _ClassVar[Role]
    FIXER: _ClassVar[Role]
    VERIFIER: _ClassVar[Role]

class ResponseFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_FORMAT_UNSPECIFIED: _ClassVar[ResponseFormat]
    TEXT: _ClassVar[ResponseFormat]
    JSON_FORMAT: _ClassVar[ResponseFormat]

class OutputFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTPUT_FORMAT_UNSPECIFIED: _ClassVar[OutputFormat]
    OUTPUT_TEXT: _ClassVar[OutputFormat]
    OUTPUT_BULLETS: _ClassVar[OutputFormat]
    OUTPUT_JSON: _ClassVar[OutputFormat]
    OUTPUT_DECISION: _ClassVar[OutputFormat]
    OUTPUT_PATCH: _ClassVar[OutputFormat]

class ResponseStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESPONSE_STATUS_UNSPECIFIED: _ClassVar[ResponseStatus]
    OK: _ClassVar[ResponseStatus]
    DENIED: _ClassVar[ResponseStatus]
    ERROR: _ClassVar[ResponseStatus]

class AnswerSource(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ANSWER_SOURCE_UNSPECIFIED: _ClassVar[AnswerSource]
    CACHED: _ClassVar[AnswerSource]
    POLICY: _ClassVar[AnswerSource]
    USER_HISTORY: _ClassVar[AnswerSource]

class DelegationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DELEGATION_STATUS_UNSPECIFIED: _ClassVar[DelegationStatus]
    DELEGATION_OK: _ClassVar[DelegationStatus]
    DELEGATION_ERROR: _ClassVar[DelegationStatus]

class ArtifactKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ARTIFACT_KIND_UNSPECIFIED: _ClassVar[ArtifactKind]
    PATCH: _ClassVar[ArtifactKind]
    COMMIT: _ClassVar[ArtifactKind]
    REPORT: _ClassVar[ArtifactKind]
    FILE: _ClassVar[ArtifactKind]
    URL: _ClassVar[ArtifactKind]
ROLE_UNSPECIFIED: Role
PLANNER: Role
IMPLEMENTER: Role
REVIEWER: Role
FIXER: Role
VERIFIER: Role
RESPONSE_FORMAT_UNSPECIFIED: ResponseFormat
TEXT: ResponseFormat
JSON_FORMAT: ResponseFormat
OUTPUT_FORMAT_UNSPECIFIED: OutputFormat
OUTPUT_TEXT: OutputFormat
OUTPUT_BULLETS: OutputFormat
OUTPUT_JSON: OutputFormat
OUTPUT_DECISION: OutputFormat
OUTPUT_PATCH: OutputFormat
RESPONSE_STATUS_UNSPECIFIED: ResponseStatus
OK: ResponseStatus
DENIED: ResponseStatus
ERROR: ResponseStatus
ANSWER_SOURCE_UNSPECIFIED: AnswerSource
CACHED: AnswerSource
POLICY: AnswerSource
USER_HISTORY: AnswerSource
DELEGATION_STATUS_UNSPECIFIED: DelegationStatus
DELEGATION_OK: DelegationStatus
DELEGATION_ERROR: DelegationStatus
ARTIFACT_KIND_UNSPECIFIED: ArtifactKind
PATCH: ArtifactKind
COMMIT: ArtifactKind
REPORT: ArtifactKind
FILE: ArtifactKind
URL: ArtifactKind

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
    __slots__ = ("worktree_id", "agent_instance_id", "parent_agent_instance_id", "role", "created_at", "retry_of_agent_instance_id")
    WORKTREE_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    RETRY_OF_AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    worktree_id: str
    agent_instance_id: str
    parent_agent_instance_id: str
    role: Role
    created_at: _timestamp_pb2.Timestamp
    retry_of_agent_instance_id: str
    def __init__(self, worktree_id: _Optional[str] = ..., agent_instance_id: _Optional[str] = ..., parent_agent_instance_id: _Optional[str] = ..., role: _Optional[_Union[Role, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., retry_of_agent_instance_id: _Optional[str] = ...) -> None: ...

class AskUserPayload(_message.Message):
    __slots__ = ("question", "choices", "default_value", "why", "response_format", "timeout_seconds")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    CHOICES_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    WHY_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    question: str
    choices: _containers.RepeatedScalarFieldContainer[str]
    default_value: str
    why: str
    response_format: ResponseFormat
    timeout_seconds: int
    def __init__(self, question: _Optional[str] = ..., choices: _Optional[_Iterable[str]] = ..., default_value: _Optional[str] = ..., why: _Optional[str] = ..., response_format: _Optional[_Union[ResponseFormat, str]] = ..., timeout_seconds: _Optional[int] = ...) -> None: ...

class DelegatePayload(_message.Message):
    __slots__ = ("delegate_to", "task")
    DELEGATE_TO_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    delegate_to: Role
    task: Task
    def __init__(self, delegate_to: _Optional[_Union[Role, str]] = ..., task: _Optional[_Union[Task, _Mapping]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ("text", "inputs", "return_format")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    RETURN_FORMAT_FIELD_NUMBER: _ClassVar[int]
    text: str
    inputs: TaskInputs
    return_format: OutputFormat
    def __init__(self, text: _Optional[str] = ..., inputs: _Optional[_Union[TaskInputs, _Mapping]] = ..., return_format: _Optional[_Union[OutputFormat, str]] = ...) -> None: ...

class TaskInputs(_message.Message):
    __slots__ = ("artifact_refs", "repo_path", "extra")
    ARTIFACT_REFS_FIELD_NUMBER: _ClassVar[int]
    REPO_PATH_FIELD_NUMBER: _ClassVar[int]
    EXTRA_FIELD_NUMBER: _ClassVar[int]
    artifact_refs: _containers.RepeatedScalarFieldContainer[str]
    repo_path: str
    extra: _struct_pb2.Struct
    def __init__(self, artifact_refs: _Optional[_Iterable[str]] = ..., repo_path: _Optional[str] = ..., extra: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class DenDenResponse(_message.Message):
    __slots__ = ("denden_version", "request_id", "status", "error", "ask_user_result", "delegate_result", "meta")
    DENDEN_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ASK_USER_RESULT_FIELD_NUMBER: _ClassVar[int]
    DELEGATE_RESULT_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    denden_version: str
    request_id: str
    status: ResponseStatus
    error: ErrorDetail
    ask_user_result: AskUserResult
    delegate_result: DelegateResult
    meta: ResponseMeta
    def __init__(self, denden_version: _Optional[str] = ..., request_id: _Optional[str] = ..., status: _Optional[_Union[ResponseStatus, str]] = ..., error: _Optional[_Union[ErrorDetail, _Mapping]] = ..., ask_user_result: _Optional[_Union[AskUserResult, _Mapping]] = ..., delegate_result: _Optional[_Union[DelegateResult, _Mapping]] = ..., meta: _Optional[_Union[ResponseMeta, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("immediate",)
    IMMEDIATE_FIELD_NUMBER: _ClassVar[int]
    immediate: ImmediateAnswer
    def __init__(self, immediate: _Optional[_Union[ImmediateAnswer, _Mapping]] = ...) -> None: ...

class ImmediateAnswer(_message.Message):
    __slots__ = ("text", "json", "source")
    TEXT_FIELD_NUMBER: _ClassVar[int]
    JSON_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    text: str
    json: _struct_pb2.Struct
    source: AnswerSource
    def __init__(self, text: _Optional[str] = ..., json: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., source: _Optional[_Union[AnswerSource, str]] = ...) -> None: ...

class DelegateResult(_message.Message):
    __slots__ = ("delegation",)
    DELEGATION_FIELD_NUMBER: _ClassVar[int]
    delegation: Delegation
    def __init__(self, delegation: _Optional[_Union[Delegation, _Mapping]] = ...) -> None: ...

class Delegation(_message.Message):
    __slots__ = ("output_format", "output", "summary", "artifacts", "status")
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    output_format: OutputFormat
    output: _struct_pb2.Struct
    summary: str
    artifacts: _containers.RepeatedCompositeFieldContainer[Artifact]
    status: DelegationStatus
    def __init__(self, output_format: _Optional[_Union[OutputFormat, str]] = ..., output: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., summary: _Optional[str] = ..., artifacts: _Optional[_Iterable[_Union[Artifact, _Mapping]]] = ..., status: _Optional[_Union[DelegationStatus, str]] = ...) -> None: ...

class Artifact(_message.Message):
    __slots__ = ("kind", "ref", "meta")
    class MetaEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KIND_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    META_FIELD_NUMBER: _ClassVar[int]
    kind: ArtifactKind
    ref: str
    meta: _containers.ScalarMap[str, str]
    def __init__(self, kind: _Optional[_Union[ArtifactKind, str]] = ..., ref: _Optional[str] = ..., meta: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ResponseMeta(_message.Message):
    __slots__ = ("orchestrator_action_id", "policy_flags", "sub_agent_instance_id", "applied_policy")
    ORCHESTRATOR_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    SUB_AGENT_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    APPLIED_POLICY_FIELD_NUMBER: _ClassVar[int]
    orchestrator_action_id: str
    policy_flags: _containers.RepeatedScalarFieldContainer[str]
    sub_agent_instance_id: str
    applied_policy: AppliedPolicy
    def __init__(self, orchestrator_action_id: _Optional[str] = ..., policy_flags: _Optional[_Iterable[str]] = ..., sub_agent_instance_id: _Optional[str] = ..., applied_policy: _Optional[_Union[AppliedPolicy, _Mapping]] = ...) -> None: ...

class AppliedPolicy(_message.Message):
    __slots__ = ("max_tokens", "timeout_seconds", "tools_allowed", "depth", "depth_limit")
    MAX_TOKENS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    TOOLS_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    DEPTH_LIMIT_FIELD_NUMBER: _ClassVar[int]
    max_tokens: int
    timeout_seconds: int
    tools_allowed: _containers.RepeatedScalarFieldContainer[str]
    depth: int
    depth_limit: int
    def __init__(self, max_tokens: _Optional[int] = ..., timeout_seconds: _Optional[int] = ..., tools_allowed: _Optional[_Iterable[str]] = ..., depth: _Optional[int] = ..., depth_limit: _Optional[int] = ...) -> None: ...

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
