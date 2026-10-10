<div align="center">

<img src=".github/assets/ErisPulseLogo.png" width="180" alt="ErisPulse GovReport" />

# ErisPulse GovReport

**Governance observability — stats for command execution, blocked events and usage quotas.**

Built on ErisPulse 2.9 command governance and lifecycle events. Records persist via the built-in ORM; reports render as Takumi cards.

<p>
  <a href="https://pypi.org/project/ErisPulse-GovReport/"><img src="https://img.shields.io/pypi/v/ErisPulse-GovReport?style=for-the-badge&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://pypi.org/project/ErisPulse-GovReport/"><img src="https://img.shields.io/badge/Python-3.10+-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/ErisPulse/ErisPulse-GovReport"><img src="https://img.shields.io/github/stars/ErisPulse/ErisPulse-GovReport?style=for-the-badge&logo=github&color=brightgreen" alt="Stars"></a>
  <a href="https://pepy.tech/project/ErisPulse-GovReport"><img src="https://img.shields.io/pepy/dt/ErisPulse-GovReport?style=for-the-badge&color=blue" alt="Downloads"></a>
  <a href="https://github.com/ErisPulse/ErisPulse"><img src="https://img.shields.io/badge/Powered_by-ErisPulse-FF6B9D?style=for-the-badge&logo=bookstack&logoColor=white" alt="ErisPulse"></a>
</p>

<p>
  <a href="./README.md">简体中文</a> | <a href="./README.en.md">English</a>
</p>

</div>

---

## Introduction

GovReport is a governance observability module for the [ErisPulse](https://github.com/ErisPulse/ErisPulse/) framework:

- Collects `command.executed` records (success / failure / deprecated)
- Collects `adapter.event.blocked` (middleware veto) and `scope.blocked` records
- Reads `usage_limit` quota counters (the `erispulse.usage` storage keys) and shows consumption against declared limits
- Enumerates governance declarations of all commands (cooldown / rate_limit / usage_limit / deprecated)
- Persists records with the built-in ORM (`Model` / `Field`), auto-purged by retention days
- Renders reports as Takumi image cards, falling back to text

Requires ErisPulse >= 2.9.0.

---

## Installation

```bash
epsdk install ErisPulse-GovReport
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/gov` | Show usage |
| `/gov stats [window]` | Command execution stats (top commands / success rate / deprecated uses); window like `24h`, `7d`, default `24h` |
| `/gov user <user_id> [window]` | Per-user stats |
| `/gov blocked [window]` | Blocked event stats (middleware veto / scope) |
| `/gov usage` | Usage quota report (used/limit + period + scope) |
| `/gov list [command]` | Governance declarations (filter by command name) |
| `/gov purge <days>` | Purge records older than N days |

All commands require framework master permission.

---

## Usage

```python
from ErisPulse.Core.Event import command

@command("translate", cooldown="30s", rate_limit="5/minute",
         usage_limit="100/day", usage_limit_key="user", help="translate")
async def translate_handler(event):
    await event.reply("result")

@command("oldcmd", deprecated="use /translate", deprecated_reject=True)
async def old_handler(event):
    ...
```

---

## Configuration

```toml
[GovReport]
collect_command_calls = true    # collect command executions
collect_blocked = true          # collect blocked events
retention_days = 30             # retention days (0 = keep forever)
top_n = 10                      # max entries per report
render_card = true              # render reports as image cards
theme = "doodle"                  # card style (doodle/editorial)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `collect_command_calls` | bool | `true` | Collect `command.executed` |
| `collect_blocked` | bool | `true` | Collect middleware/scope blocks |
| `retention_days` | int | `30` | Retention days (0 = keep forever; purged on start and daily) |
| `top_n` | int | `10` | Max entries per report |
| `render_card` | bool | `true` | Render reports as image cards |
| `theme` | str | `doodle` | Card style (doodle/editorial) |

---

## Notes

1. Quota consumption reads the governance storage keys (`erispulse.usage`), surviving restarts
2. Cooldown/rate-limit hits are silent by default and not collected (use DispatchTrace of ErisPulse-Testing to debug a single command)
3. Records go to the framework storage backend (SQLite / MySQL / PostgreSQL per storage config)

---

## References

- [ErisPulse](https://github.com/ErisPulse/ErisPulse/)
- [Command governance docs](https://github.com/ErisPulse/ErisPulse/tree/main/docs/zh-CN/getting-started/event-handling.md)
- [ORM docs](https://github.com/ErisPulse/ErisPulse/tree/main/docs/zh-CN/developer-guide/orm.md)
