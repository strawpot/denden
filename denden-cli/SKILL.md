---
name: denden-cli
description: "Use the denden Go CLI to communicate with the orchestrator via gRPC"
metadata:
  strawpot:
    tools:
      denden:
        description: DenDen CLI for orchestrator communication
        install:
          macos: curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/install.sh | sh
          linux: curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/install.sh | sh
          windows: curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/install.sh | sh
---

# DenDen CLI

Use `denden send <json>` to ask the user a question or delegate work to a sub-agent. The payload must contain exactly one of `askUser` or `delegate`.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/install.sh | sh
```

Or set a custom install directory:

```bash
INSTALL_DIR=./bin curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/install.sh | sh
```

Supports Linux, macOS, and Windows (via MSYS/Git Bash). Binaries are available for x86_64 and ARM64.

## Ask the user a question

```bash
denden send '{"askUser":{"question":"Which language should the module use?","choices":["Python","Go"]}}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | yes | The question to ask |
| `choices` | string[] | no | Constrained set of answers |
| `defaultValue` | string | no | Pre-selected answer |
| `why` | string | no | Explanation of why the question is needed |
| `responseFormat` | Format | no | `TEXT` (default) or `JSON` |

## Delegate work to a sub-agent

```bash
denden send '{"delegate":{"delegateTo":"implementer","task":{"text":"implement auth module","returnFormat":"TEXT"}}}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `delegateTo` | string | yes | Target role |
| `task.text` | string | yes | Task description |
| `task.artifactRefs` | string[] | no | References to input artifacts |
| `task.extra` | object | no | Additional key-value context |
| `task.returnFormat` | Format | no | Expected output format |

**Roles (examples):** `planner`, `implementer`, `reviewer`, `fixer`, `verifier`

**Formats:** `TEXT` (default), `JSON`

## Guidelines

- Use `choices` in `askUser` when the set of valid answers is known.
- Check the exit code after every invocation; non-zero means the request was denied or failed.
