from ErisPulse import sdk

from GovReport.Models import BlockEvent, CommandCall


async def test_collect_command_executed(govbot):
    await sdk.lifecycle.emit("command.executed", {
        "command": "roll",
        "args": ["3"],
        "platform": "test",
        "user_id": "tester",
        "success": True,
    })
    rows = await CommandCall.where(CommandCall.command == "roll").all()
    assert len(rows) == 1
    assert rows[0].platform == "test"
    assert rows[0].user_id == "tester"
    assert rows[0].success is True
    assert rows[0].error == ""


async def test_collect_deprecated_failure(govbot):
    await sdk.lifecycle.emit("command.executed", {
        "command": "oldcmd",
        "platform": "test",
        "user_id": "tester",
        "success": False,
        "error": "deprecated",
    })
    rows = await CommandCall.where(CommandCall.command == "oldcmd").all()
    assert len(rows) == 1
    assert rows[0].success is False
    assert rows[0].error == "deprecated"


async def test_collect_middleware_blocked(govbot):
    await sdk.lifecycle.emit("adapter.event.blocked", {
        "middleware": "firewall",
        "platform": "test",
        "event_type": "message",
        "detail_type": "group",
        "event": {"user_id": "banned_user"},
    })
    rows = await BlockEvent.where(BlockEvent.source == "middleware").all()
    assert len(rows) == 1
    assert rows[0].middleware == "firewall"
    assert rows[0].user_id == "banned_user"
    assert rows[0].detail_type == "group"


async def test_collect_scope_blocked(govbot):
    await sdk.lifecycle.emit("scope.blocked", {
        "dimension": "module",
        "module": "NoisyModule",
        "platform": "test",
        "bot_id": "test_bot",
        "session_id": "group_123",
    })
    rows = await BlockEvent.where(BlockEvent.source == "scope").all()
    assert len(rows) == 1
    assert rows[0].dimension == "module"
    assert rows[0].module == "NoisyModule"
    assert rows[0].session_id == "group_123"


async def test_collect_disabled_by_config(govbot):
    cfg = govbot.gov.cfg
    cfg.collect_blocked = False
    cfg.collect_command_calls = False
    govbot.gov.cfg = cfg

    await sdk.lifecycle.emit("command.executed", {
        "command": "roll", "platform": "test", "user_id": "u", "success": True,
    })
    await sdk.lifecycle.emit("adapter.event.blocked", {
        "middleware": "fw", "platform": "test", "event_type": "message", "detail_type": "", "event": {},
    })
    assert await CommandCall.count() == 0
    assert await BlockEvent.count() == 0
