import time

from ErisPulse_Testing import create_command_event

from ErisPulse import sdk

from GovReport.Models import BlockEvent, CommandCall

SEP = "\x00"


class FakeTakumi:
    def __init__(self):
        self.calls = []

    def render_html(self, body, stylesheets=None, width=None, height=None, lang=None, **kw):
        self.calls.append((body, width))
        return b"FAKEPNG"


async def _seed(govbot):
    now = time.time()
    await CommandCall.create(ts=now - 60, command="translate", platform="test", user_id="u1", success=True)
    await CommandCall.create(ts=now - 60, command="translate", platform="test", user_id="u2", success=True)
    await CommandCall.create(ts=now - 60, command="oldcmd", platform="test", user_id="u1", success=False, error="deprecated")
    await BlockEvent.create(ts=now - 10, source="middleware", middleware="firewall", platform="test", detail_type="group")
    await BlockEvent.create(ts=now - 10, source="scope", dimension="module", module="Noisy", platform="test")


async def test_stats_card_html(govbot):
    await _seed(govbot)
    stats = govbot.gov._stats
    html = await stats.command_stats_card("24h", 10, govbot.gov._viz)
    assert "命令执行统计" in html
    assert "总调用" in html
    assert "translate" in html
    assert "bar-fill" in html


async def test_blocked_card_html(govbot):
    await _seed(govbot)
    html = await govbot.gov._stats.blocked_stats_card("24h", 10, govbot.gov._viz)
    assert "事件拦截统计" in html
    assert "firewall" in html
    assert "module:Noisy" in html


async def test_usage_and_list_card_html(govbot):
    from ErisPulse.Core.Event import command

    @command("carddemo", cooldown="30s", usage_limit="50/day", deprecated="换 /new", help="t")
    async def _carddemo(event):
        await event.reply("ok")

    await sdk.storage.aset(SEP.join(("erispulse.usage", "carddemo", "test:b:u1", "2026-10-10")), 12)

    stats = govbot.gov._stats
    usage_html = await stats.usage_report_card(govbot.gov._viz)
    assert "配额消耗" in usage_html
    assert "carddemo" in usage_html
    assert "12/50" in usage_html

    list_html = stats.governance_list_card(None, govbot.gov._viz)
    assert "治理声明清单" in list_html
    assert "carddemo" in list_html
    assert "cooldown 30s" in list_html


async def test_card_render_replies_image(govbot):
    govbot.gov._viz._takumi_inst = FakeTakumi()
    cfg = govbot.gov.cfg
    cfg.render_card = True
    govbot.gov.cfg = cfg

    await _seed(govbot)
    await govbot.dispatch(create_command_event("gov stats 24h"))
    msg = govbot.last_reply
    assert any(seg.get("type") == "image" for seg in msg.segments)
    body, width = govbot.gov._viz._takumi_inst.calls[0]
    assert "命令执行统计" in body
    assert width == govbot.gov._viz.CARD_WIDTH


async def test_card_disabled_uses_text(govbot):
    govbot.gov._viz._takumi_inst = FakeTakumi()
    await _seed(govbot)
    await govbot.dispatch(create_command_event("gov stats 24h"))
    assert govbot.gov._viz._takumi_inst.calls == []
    govbot.assert_reply_contains("共 3 次")
