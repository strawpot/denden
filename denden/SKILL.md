---
name: denden
description: "Use the denden CLI to communicate with the orchestrator via gRPC. Use this skill whenever you need to ask the user a question, delegate work to another agent, store information for later recall, or check the orchestrator's health. If you see DENDEN_ADDR or DENDEN_AGENT_ID in your environment, you are running as a denden agent and should use this skill for all orchestrator interactions."
metadata:
  strawpot:
    bin:
      macos: denden
      linux: denden
      windows: denden.exe
    install:
      macos: curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/denden/install.sh | sh
      linux: curl -fsSL https://raw.githubusercontent.com/strawpot/denden/main/denden/install.sh | sh
---

# DenDen CLI

DenDen is an agent-to-orchestrator communication layer. Use `denden send <json>` to send a request to the orchestrator. The JSON payload must contain exactly one of `askUser`, `delegate`, or `remember`.

The response is printed as JSON to stdout. A non-zero exit code means the request was denied or failed — always check it.

## Environment

These variables are set by the orchestrator when it spawns you as an agent:

| Variable | Default | Description |
|---|---|---|
| `DENDEN_ADDR` | `127.0.0.1:9700` | Orchestrator gRPC address |
| `DENDEN_AGENT_ID` | — | Your agent instance ID |
| `DENDEN_PARENT_AGENT_ID` | — | Parent agent's instance ID |
| `DENDEN_RUN_ID` | — | Current run ID |
| `DENDEN_TIMEOUT` | `30s` | Request timeout |

## Ask the user a question

Use `askUser` when you need input or a decision from the user.

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

Prefer `choices` when the set of valid answers is known — it reduces ambiguity and speeds up the interaction.

## Delegate work to a sub-agent

Use `delegate` to hand off a task to another agent role.

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

## Remember information

Use `remember` to persist information for later recall across sessions.

```bash
denden send '{"remember":{"content":"The auth module uses JWT with RS256","keywords":["auth","jwt"],"scope":"project"}}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | yes | Information to remember |
| `keywords` | string[] | no | Keywords for search/indexing |
| `scope` | string | no | `global`, `project`, or `role` |

The response includes a `status` (`accepted`, `duplicate`, or `queued`) and an `entryId`.

## Check orchestrator health

```bash
denden status
```

Returns uptime and active agent counts as JSON. Useful for verifying the orchestrator is reachable before sending requests.

## Formats

`TEXT` (default) or `JSON` — applies to `responseFormat` in `askUser` and `returnFormat` in `delegate`.
