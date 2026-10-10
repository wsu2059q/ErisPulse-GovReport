import time

from ErisPulse_Testing import create_command_event

from GovReport.Models import BlockEvent, CommandCall

SEP = "\x00"


async def _seed_calls(govbot):
    now = time.time()
    await CommandCall.create(ts=now - 60, command="translate", platform="test", user_id="u1", success=True)
    await CommandCall.create(ts=now - 60, command="translate", platform="test", user_id="u2", success=True)
    await CommandCall.create(ts=now - 60, command="oldcmd", platform="test", user_id="u1", success=False, error="deprecated")


async def test_gov_usage_hint(govbot):
    await govbot.dispatch(create_command_event("gov"))
    govbot.assert_reply_contains("用法")


async def test_gov_stats(govbot):
    await _seed_calls(govbot)
    await govbot.dispatch(create_command_event("gov stats 24h"))
    reply = govbot.last_reply.text
    assert "共 3 次" in reply
    assert "成功 2" in reply
    assert "废弃命令使用 1 次" in reply
    assert "translate: 2" in reply


async def test_gov_stats_empty_window(govbot):
    await govbot.dispatch(create_command_event("gov stats 24h"))
    govbot.assert_reply_contains("没有命令记录")


async def test_gov_stats_invalid_window(govbot):
    await govbot.dispatch(create_command_event("gov stats bogus"))
    govbot.assert_reply_contains("无效的时间窗口")


async def test_gov_user(govbot):
    await _seed_calls(govbot)
    await govbot.dispatch(create_command_event("gov user u1 24h"))
    reply = govbot.last_reply.text
    assert "共 2 次" in reply
    assert "translate: 1" in reply
    assert "oldcmd: 1" in reply


async def test_gov_user_empty(govbot):
    await govbot.dispatch(create_command_event("gov user nobody 24h"))
    govbot.assert_reply_contains("没有记录")


async def test_gov_blocked(govbot):
    now = time.time()
    await BlockEvent.create(ts=now - 10, source="middleware", middleware="firewall", platform="test",
                            detail_type="group", user_id="b1")
    await BlockEvent.create(ts=now - 10, source="middleware", middleware="firewall", platform="test",
                            detail_type="private", user_id="b2")
    await BlockEvent.create(ts=now - 10, source="scope", dimension="module", module="Noisy",
                            platform="test", session_id="g1")
    await govbot.dispatch(create_command_event("gov blocked 24h"))
    reply = govbot.last_reply.text
    assert "共 3 次" in reply
    assert "by_source: middleware=2 scope=1" in reply
    assert "middleware:firewall: 2" in reply
    assert "scope:module:Noisy: 1" in reply


async def test_gov_usage(govbot):
    from ErisPulse import sdk

    from ErisPulse.Core.Event import command

    @command("limited", usage_limit="100/day", usage_limit_key="user", help="配额测试命令")
    async def _limited(event):
        await event.reply("ok")

    key = SEP.join(("erispulse.usage", "limited", "test:test_bot:tester", "2026-10-10"))
    await sdk.storage.aset(key, 78)

    await govbot.dispatch(create_command_event("gov usage"))
    reply = govbot.last_reply.text
    assert "活跃键 1 个" in reply
    assert "limited: 78/100(day)" in reply
    assert "period=2026-10-10" in reply
    assert "scope=test:test_bot:tester" in reply


async def test_gov_usage_empty(govbot):
    await govbot.dispatch(create_command_event("gov usage"))
    govbot.assert_reply_contains("没有配额消耗记录")


async def test_gov_list(govbot):
    from ErisPulse.Core.Event import command

    @command("govdemo", cooldown="30s", rate_limit="5/minute", usage_limit="100/day",
             deprecated="请用 /newcmd", help="治理声明测试")
    async def _govdemo(event):
        await event.reply("ok")

    await govbot.dispatch(create_command_event("gov list govdemo"))
    reply = govbot.last_reply.text
    assert "govdemo:" in reply
    assert "cooldown=30s(user)" in reply
    assert "rate=5/60s(user)" in reply
    assert "usage=100/day(user)" in reply
    assert "deprecated[notice]=请用 /newcmd" in reply


async def test_gov_list_empty(govbot):
    await govbot.dispatch(create_command_event("gov list __no_match__"))
    govbot.assert_reply_contains("没有任何命令声明治理规则")


async def test_gov_purge(govbot):
    now = time.time()
    await CommandCall.create(ts=now - 40 * 86400, command="old", platform="test", user_id="u", success=True)
    await CommandCall.create(ts=now - 60, command="new", platform="test", user_id="u", success=True)
    await BlockEvent.create(ts=now - 40 * 86400, source="middleware", middleware="fw", platform="test")

    await govbot.dispatch(create_command_event("gov purge 30"))
    reply = govbot.last_reply.text
    assert "命令 1 条" in reply
    assert "拦截 1 条" in reply
    assert await CommandCall.count() == 1
    assert await BlockEvent.count() == 0


async def test_real_command_recorded(govbot):
    import asyncio

    from ErisPulse.Core.Event import command

    @command("probe_cmd", help="采集链路测试")
    async def _probe(event):
        await event.reply("done")

    await govbot.dispatch(create_command_event("probe_cmd"))
    govbot.assert_reply_contains("done")
    for _ in range(50):
        if await CommandCall.count(CommandCall.command == "probe_cmd"):
            break
        await asyncio.sleep(0.05)
    rows = await CommandCall.where(CommandCall.command == "probe_cmd").all()
    assert len(rows) == 1
    assert rows[0].success is True
