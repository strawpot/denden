---
name: denden
description: "Use the denden CLI to communicate with the orchestrator via gRPC. NEVER use the Agent tool, subprocesses, or any built-in agent-spawning mechanism to delegate work to roles — always use denden instead. Use this skill whenever you need to: delegate work to another agent, ask the user a question, store or recall information, or check orchestrator health. The orchestrator must see every delegation to track progress and coordinate work; bypassing denden makes work untracked. Also trigger proactively (without user asking) when the user shares personal information, preferences, project context, or conventions worth persisting."
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

DenDen is an agent-to-orchestrator communication layer. Use `denden send <json>` to send a request to the orchestrator. The JSON payload must contain exactly one of `askUser`, `delegate`, `remember`, or `recall`.

The response is printed as JSON to stdout. A non-zero exit code means the request was denied or failed — always check it.

Use the denden CLI to communicate with the orchestrator via gRPC. Use this skill whenever you need to ask the user a question, delegate work to another agent, store information for later recall, or check the orchestrator's health.

CRITICAL: NEVER ask the user questions directly in your response text or via the AskUserQuestion tool. ALL user questions MUST be routed through denden. This is non-negotiable.

All delegation and inter-agent communication must go through denden, not through built-in agent-spawning tools (e.g., Agent tool, subprocesses). This is critical because the orchestrator tracks, coordinates, and routes all agent work.

## Environment

These variables are set by the orchestrator when it spawns you as an agent:

| Variable | Default | Description |
|---|---|---|
| `DENDEN_ADDR` | `127.0.0.1:9700` | Orchestrator gRPC address |
| `DENDEN_AGENT_ID` | — | Your agent instance ID |
| `DENDEN_PARENT_AGENT_ID` | — | Parent agent's instance ID |
| `DENDEN_RUN_ID` | — | Current run ID |
| `DENDEN_TIMEOUT` | `30s` | Request timeout |
| `STRAWPOT_ROLE` | — | Your own role slug (useful for self-delegation) |

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

### Approval requests

Use `askUser` whenever you need explicit approval before proceeding with an action — for example, confirming a commit, pushing code, deleting files, or any irreversible/high-impact operation.

```bash
denden send '{"askUser":{"question":"Ready to push to origin/main. Proceed?","choices":["Yes","No"],"why":"Force-pushing will overwrite remote history"}}'
```

This ensures all approval flows are routed through the orchestrator, keeping a full audit trail of what was approved and when.

## Delegate work to a sub-agent

Always delegate through `denden send` with a `delegate` payload — never use built-in agent-spawning tools (the Agent tool, subprocesses, or similar). The orchestrator needs to see every delegation request so it can track progress, coordinate parallel work, and route tasks to the right agent. Bypassing denden means the orchestrator loses visibility and the work becomes untracked.

```bash
denden send '{"delegate":{"delegateTo":"code-reviewer","task":{"text":"Review the auth module for security issues","returnFormat":"TEXT"}}}'
```

**`delegateTo` must exactly match the role slug** listed in the **Delegation** section of your prompt (e.g., `code-reviewer`, not `Code Reviewer`, `codeReviewer`, or `reviewer`). Spelling, hyphens, and case must match exactly. If you use an unrecognized slug the request will fail with `DENY_ROLE_NOT_ALLOWED`.

| Field | Type | Required | Description |
|---|---|---|---|
| `delegateTo` | string | yes | Exact role slug, or empty string `""` for self-delegation |
| `task.text` | string | yes | Task description |
| `task.artifactRefs` | string[] | no | References to input artifacts |
| `task.extra` | object | no | Additional key-value context |
| `task.returnFormat` | Format | no | Expected output format (`TEXT` or `JSON`) |

### Self-delegation

To delegate to a fresh instance of your own role, set `delegateTo` to an empty string. The orchestrator resolves it to your role slug automatically. This is useful for iterative self-improvement workflows.

```bash
denden send '{"delegate":{"delegateTo":"","task":{"text":"Evaluate this output: ..."}}}'
```

You can also use `$STRAWPOT_ROLE` to reference your own role slug explicitly:

```bash
denden send "{\"delegate\":{\"delegateTo\":\"$STRAWPOT_ROLE\",\"task\":{\"text\":\"Evaluate this output: ...\"}}}"
```

Both approaches are equivalent. Self-delegation consumes one level of delegation depth — `max_depth` prevents infinite loops.

### Reading the response

On success (`"status": "OK"`), the sub-agent's output is in `delegateResult`:

```json
// TEXT format (default)
{
  "status": "OK",
  "delegateResult": {
    "text": "The auth module looks secure. No issues found."
  }
}
```

```json
// JSON format (when returnFormat is "JSON")
{
  "status": "OK",
  "delegateResult": {
    "json": { "issues": [], "verdict": "pass" }
  }
}
```

Extract the text output in bash:

```bash
response=$(denden send '{"delegate":{"delegateTo":"code-reviewer","task":{"text":"Review auth module"}}}')
output=$(echo "$response" | python3 -c "import json,sys; print(json.load(sys.stdin).get('delegateResult',{}).get('text',''))")
```

Feed one sub-agent's output as input to the next by passing `$output` in the next delegation's `task.text`.

### Error recovery

On failure (exit code non-zero), `status` is `"DENIED"` or `"ERROR"`:

```json
{
  "status": "DENIED",
  "error": {
    "code": "DENY_DEPTH_LIMIT",
    "message": "max delegation depth exceeded",
    "retryable": false
  }
}
```

| `error.code` | Meaning | What to do |
|---|---|---|
| `DENY_ROLE_NOT_ALLOWED` | Role slug not in your Delegation list | Check the exact slug in your prompt's Delegation section |
| `DENY_DEPTH_LIMIT` | Delegation chain too deep | Handle the work directly or simplify the chain |
| `DENY_DELEGATIONS_LIMIT` | Session delegation quota reached | Handle remaining work directly |
| `DENY_BUDGET_EXCEEDED` | Budget exceeded | Reduce scope or use `askUser` to request more budget |
| `ERR_SUBAGENT_FAILURE` | Sub-agent exited with non-zero code | Retry with a clearer task description, or escalate via `askUser` |

If `"retryable": true`, you may retry the same request once. Otherwise escalate to the user.

### Parallel delegation

Independent tasks can run in parallel — fire multiple `denden send` calls concurrently with `&` and collect results:

```bash
# Fire both delegations in background
denden send '{"delegate":{"delegateTo":"code-reviewer","task":{"text":"Review auth module"}}}' > /tmp/review.json &
denden send '{"delegate":{"delegateTo":"code-simplifier","task":{"text":"Simplify utils.py"}}}' > /tmp/simplify.json &

# Wait for both to complete
wait

# Read results
review_output=$(python3 -c "import json; print(json.load(open('/tmp/review.json')).get('delegateResult',{}).get('text',''))")
simplify_output=$(python3 -c "import json; print(json.load(open('/tmp/simplify.json')).get('delegateResult',{}).get('text',''))")
```

Each `denden send` blocks until the sub-agent finishes. Running them with `&` gives true parallelism and significantly reduces total wall time for independent stages.

## Remember information

Use `remember` to persist information for later recall across sessions.

```bash
denden send '{"remember":{"content":"The auth module uses JWT with RS256","keywords":["auth","jwt"],"scope":"project"}}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `content` | string | yes | Information to remember |
| `keywords` | string[] | no | Keywords for relevance-based retrieval |
| `scope` | string | no | `global`, `project`, or `role` (default: `project`) |

**Scope semantics:**

| Scope | Visible to | When to use |
|---|---|---|
| `project` | All sessions in this project | Architecture decisions, codebase conventions, known issues in this repo |
| `role` | All sessions using this role in this project | Role-specific patterns, preferred tools or libraries for this project |
| `global` | All sessions everywhere | Personal preferences, universal standards, cross-project conventions |

When in doubt, use `project`. Use `global` only for facts that apply regardless of which project you're working in.

The response includes a `status` (`accepted`, `duplicate`, or `queued`) and an `entryId`.

### Proactive memory

Automatically call `denden send` with a `remember` payload (without the user asking) whenever:

1. **Identity/preferences** — User shares their name, role, title, team, preferences, or how they like things done
2. **Project context** — User mentions project names, repo purposes, tech stack choices, or architectural decisions
3. **Conventions** — User corrects you or states a preferred style/pattern/workflow
4. **Key relationships** — User mentions stakeholders, team members, or reporting structure
5. **Recurring tasks** — User describes processes they do regularly

Do NOT auto-remember:
- Transient/one-off information (e.g., "run this command")
- Information that's already stored (check for duplicates)
- Sensitive data (passwords, tokens, secrets)

Use `global` scope for identity/preferences, `project` scope for repo-specific context.

### Auto-remember triggers

BEFORE responding to any user message, scan for the following and call `remember` immediately:

- User states personal facts (name, role, company, team, preferences)
- User shares goals, plans, or career aspirations
- User expresses preferences ("I prefer X", "I like Y")
- User corrects you about something personal
- User shares project context, tech stack choices, or architectural decisions
- Any information that would be useful in a future session

Do this BEFORE writing your main response — treat it as a pre-response step.

## Recall stored information

Use `recall` to query previously stored memories on-demand. This is useful when your task evolves mid-session and you need context that wasn't pre-loaded at spawn time.

```bash
denden send '{"recall":{"query":"auth module JWT configuration","scope":"project","maxResults":5}}'
```

| Field | Type | Required | Description |
|---|---|---|---|
| `query` | string | yes | Free-text query scored against stored keywords |
| `keywords` | string[] | no | Explicit keyword filter (narrows results) |
| `scope` | string | no | `global`, `project`, or `role` (default: searches all scopes) |
| `maxResults` | int | no | Maximum entries to return (default: 10) |

The response contains matching entries sorted by relevance:

```json
{
  "status": "OK",
  "recallResult": {
    "entries": [
      {
        "entryId": "k_a1b2c3d4",
        "content": "The auth module uses JWT with RS256",
        "keywords": ["auth", "jwt"],
        "scope": "project",
        "score": 0.85
      }
    ]
  }
}
```

Use `recall` when:
- Your task changes direction and you need context not provided at spawn
- You want to check what's already stored before calling `remember` (avoids duplicates)
- You need to reference information another agent stored earlier in the session

## Check orchestrator health

```bash
denden status
```

Returns uptime and active agent counts as JSON. Useful for verifying the orchestrator is reachable before sending requests.

## Formats

`TEXT` (default) or `JSON` — applies to `responseFormat` in `askUser` and `returnFormat` in `delegate`.
