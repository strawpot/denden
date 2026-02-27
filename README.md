# denden

Agent-to-orchestrator communication layer. A gRPC transport where agents call back to the orchestrator via the `denden` CLI.

```
Orchestrator (Python gRPC server)
  ├── spawns agents as subprocesses
  └── handles ask_user / delegate requests
         ▲
         │ gRPC (localhost)
         │
     denden CLI (Go binary)
       └── called by agents to send requests
```

## Components

| Component | Language | Path |
|---|---|---|
| CLI client | Go | `cli/` |
| Server library | Python | `server/` |
| Protocol | Protobuf | `proto/denden.proto` |

## Quick start

### Install the server

```bash
cd server
pip install -e '.[dev]'
```

### Build the CLI

```bash
cd cli
go build -o denden .
```

### Run the server

```bash
denden-server --verbose
```

### Use the CLI

```bash
# Health check
./cli/denden status

# Ask user a question
./cli/denden send '{
  "askUser": {
    "question": "Which language?",
    "choices": ["Python", "Go", "Rust"]
  }
}'

# Delegate to a sub-agent
./cli/denden send '{
  "delegate": {
    "delegateTo": "implementer",
    "task": {
      "text": "implement auth module",
      "returnFormat": "TEXT"
    }
  }
}'
```

The CLI auto-fills `request_id`, `denden_version`, `trace.created_at`, and trace fields from environment variables.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `DENDEN_ADDR` | `127.0.0.1:9700` | Server address |
| `DENDEN_AGENT_ID` | | Agent instance ID (set by orchestrator) |
| `DENDEN_PARENT_AGENT_ID` | | Parent agent instance ID |
| `DENDEN_RUN_ID` | | Run ID |
| `DENDEN_TIMEOUT` | `30s` | CLI request timeout |

## Protocol

Single `.proto` file at `proto/denden.proto`. Two RPCs:

- **Send** — dispatches `ask_user` or `delegate` requests (oneof payload)
- **Status** — health check

Response statuses: `OK`, `DENIED`, `ERROR`.

### Regenerate stubs

```bash
make proto
```

Requires `protoc`, `protoc-gen-go`, `protoc-gen-go-grpc`, and `grpcio-tools`.

## Server as a library

```python
from denden import DenDenServer, ok_response
from denden.gen import denden_pb2

server = DenDenServer(addr="127.0.0.1:9700")

def handle_ask_user(request):
    answer = input(request.ask_user.question + " ")
    return ok_response(
        request.request_id,
        ask_user_result=denden_pb2.AskUserResult(text=answer),
    )

server.on_ask_user(handle_ask_user)
server.on_delegate(my_delegate_handler)
server.run()
```

### Dynamic modules

The server CLI supports loading modules at startup:

```bash
denden-server --load-module my_custom_module
```

Modules must expose a `module` attribute or `create_module()` function returning a `denden.Module` subclass.

## License

MIT
