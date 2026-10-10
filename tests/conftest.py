import pytest

from GovReport.Core import Main

SEP = "\x00"


@pytest.fixture(scope="session", autouse=True)
def _storage_teardown():
    yield
    from ErisPulse import sdk

    try:
        sdk.storage.close()
    except Exception:
        pass


async def _purge_usage_keys():
    from ErisPulse import sdk

    root = await sdk.storage.aget("erispulse")
    if not isinstance(root, dict):
        return
    for k in list(root):
        if isinstance(k, str) and k.startswith("usage" + SEP):
            await sdk.storage.adelete("erispulse." + k)


@pytest.fixture
async def govbot(make_testbot):
    from ErisPulse import i18n

    prev_lang = i18n.get_language()
    i18n.set_language("zh-CN")

    async with make_testbot(config={"ErisPulse.master.users": {"test": ["tester"]}}) as bot:
        await bot.load_module(Main)

        from ErisPulse import module as module_mgr

        gov = module_mgr.get("GovReport")

        cfg = gov.cfg
        cfg.enabled = True
        cfg.collect_command_calls = True
        cfg.collect_blocked = True
        cfg.retention_days = 0
        cfg.top_n = 10
        cfg.render_card = False
        gov.cfg = cfg

        from GovReport.Models import BlockEvent, CommandCall

        await CommandCall.delete_all()
        await BlockEvent.delete_all()
        await _purge_usage_keys()

        bot.gov = gov
        yield bot

        await CommandCall.delete_all()
        await BlockEvent.delete_all()
        await _purge_usage_keys()

    i18n.set_language(prev_lang)
