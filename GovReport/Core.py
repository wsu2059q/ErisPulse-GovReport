import asyncio
import time

from ErisPulse import i18n, sdk
from ErisPulse.Core import Depends
from ErisPulse.Core.Bases import BaseModule, ModuleMeta
from ErisPulse.Core.Event import command
from ErisPulse.loaders import ModuleLoadStrategy

from .Config import GovReportConfig
from .I18n import GovReportI18n
from .Models import BlockEvent, CommandCall
from .Stats import GovStatsService, parse_window
from .Visualizer import CardVisualizer


def get_stats_service(event):
    from ErisPulse import module as module_mgr

    inst = module_mgr.get("GovReport")
    if inst is None:
        raise RuntimeError("GovReport not loaded")
    return inst._stats


class Main(BaseModule):

    ConfigClass = GovReportConfig
    I18nClass = GovReportI18n

    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("GovReport")
        self._stats = GovStatsService(self.logger)
        self._viz = CardVisualizer(sdk, self.logger)
        self._daily_task = None

    @staticmethod
    def get_load_strategy() -> ModuleLoadStrategy:
        return ModuleLoadStrategy(lazy_load=False, priority=20)

    @staticmethod
    def get_meta() -> ModuleMeta:
        return ModuleMeta(
            name="GovReport",
            description="治理观测模块：采集命令执行与事件拦截记录，输出统计报表与配额消耗",
            version="0.1.0",
            author="ErisPulse-devs",
            group="运维",
            tags=["治理", "统计", "ORM", "观测"],
            min_sdk_version="2.9.0",
        )

    async def on_load(self, event: dict) -> bool:
        if not self.cfg.enabled:
            self.logger.info("治理观测未启用（enabled=false）")
            return True

        await CommandCall.create_table()
        await BlockEvent.create_table()
        await self._stats.purge_expired(self.cfg.retention_days)

        self._register_collectors()
        self._register_commands()
        self._daily_task = self.spawn(self._daily_purge_loop())
        self.logger.info(i18n.t("GovReport.module_loaded", event=event))
        return True

    async def on_unload(self, event: dict) -> bool:
        if self._daily_task is not None:
            self._daily_task.cancel()
            await asyncio.gather(self._daily_task, return_exceptions=True)
            self._daily_task = None
        self.logger.info(i18n.t("GovReport.module_unloaded", event=event))
        return True

    async def _daily_purge_loop(self):
        while True:
            await asyncio.sleep(86400)
            try:
                await self._stats.purge_expired(self.cfg.retention_days)
            except Exception as e:
                self.logger.warning(f"每日清理失败: {e}")

    def _register_collectors(self):
        @sdk.lifecycle.on("command.executed")
        async def _on_command_executed(data):
            if not self.cfg.collect_command_calls:
                return
            try:
                await CommandCall.create(
                    ts=time.time(),
                    command=str(data.get("command", ""))[:128],
                    platform=str(data.get("platform", ""))[:64],
                    user_id=str(data.get("user_id", ""))[:128],
                    success=bool(data.get("success")),
                    error=str(data.get("error", "") or "")[:255],
                )
            except Exception as e:
                self.logger.warning(f"记录命令执行失败: {e}")

        @sdk.lifecycle.on("adapter.event.blocked")
        async def _on_event_blocked(data):
            if not self.cfg.collect_blocked:
                return
            raw = data.get("event") or {}
            try:
                await BlockEvent.create(
                    ts=time.time(),
                    source="middleware",
                    middleware=str(data.get("middleware", ""))[:128],
                    platform=str(data.get("platform", ""))[:64],
                    detail_type=str(data.get("detail_type", ""))[:64],
                    user_id=str(raw.get("user_id", "") or "")[:128],
                )
            except Exception as e:
                self.logger.warning(f"记录拦截事件失败: {e}")

        @sdk.lifecycle.on("scope.blocked")
        async def _on_scope_blocked(data):
            if not self.cfg.collect_blocked:
                return
            try:
                await BlockEvent.create(
                    ts=time.time(),
                    source="scope",
                    dimension=str(data.get("dimension", ""))[:16],
                    module=str(data.get("module", "") or "")[:128],
                    platform=str(data.get("platform", ""))[:64],
                    user_id=str(data.get("user_id", "") or "")[:128],
                    session_id=str(data.get("session_id", "") or "")[:128],
                )
            except Exception as e:
                self.logger.warning(f"记录作用域拦截失败: {e}")

    async def _reply_card(self, event, html, fallback_text: str):
        if self.cfg.render_card:
            png = await self._viz.render(html, theme=self.cfg.theme)
            if png is not None:
                try:
                    await event.reply(png, method="Image")
                    return
                except Exception as e:
                    self.logger.warning(f"图片回复失败，降级文本: {e}")
        await event.reply(fallback_text)

    def _register_commands(self):
        @command("gov", master=True, help="治理观测")
        async def gov_handler(event):
            await event.reply(
                "用法: /gov stats [窗口] | /gov user <用户ID> [窗口] | /gov blocked [窗口] | "
                "/gov usage | /gov list [命令] | /gov purge <天数>"
            )

        @command("gov stats", master=True, help="命令执行统计", args="[window:str=24h]")
        async def gov_stats_handler(event, window: str = "24h", stats=Depends(get_stats_service)):
            secs = parse_window(window)
            if secs is None:
                await event.reply(i18n.t("GovReport.invalid_window", window=window))
                return
            await self._reply_card(
                event,
                await stats.command_stats_card(window, self.cfg.top_n, self._viz),
                await stats.command_stats(secs, window, self.cfg.top_n),
            )

        @command("gov user", master=True, help="单用户统计", args="<user_id:str> [window:str=24h]")
        async def gov_user_handler(event, user_id: str, window: str = "24h"):
            secs = parse_window(window)
            if secs is None:
                await event.reply(i18n.t("GovReport.invalid_window", window=window))
                return
            await event.reply(await self._stats.user_stats(user_id, secs, window, self.cfg.top_n))

        @command("gov blocked", master=True, help="拦截统计", args="[window:str=24h]")
        async def gov_blocked_handler(event, window: str = "24h"):
            secs = parse_window(window)
            if secs is None:
                await event.reply(i18n.t("GovReport.invalid_window", window=window))
                return
            await self._reply_card(
                event,
                await self._stats.blocked_stats_card(window, self.cfg.top_n, self._viz),
                await self._stats.blocked_stats(secs, window, self.cfg.top_n),
            )

        @command("gov usage", master=True, help="配额消耗报表")
        async def gov_usage_handler(event):
            await self._reply_card(
                event,
                await self._stats.usage_report_card(self._viz),
                await self._stats.usage_report(),
            )

        @command("gov list", master=True, help="治理声明清单", args="[cmd:str]")
        async def gov_list_handler(event, cmd: str = ""):
            await self._reply_card(
                event,
                self._stats.governance_list_card(cmd or None, self._viz),
                self._stats.governance_list(cmd or None),
            )

        @command("gov purge", master=True, help="清理旧记录", args="<days:int>")
        async def gov_purge_handler(event, days: int):
            if days <= 0:
                await event.reply(i18n.t("GovReport.invalid_window", window=str(days)))
                return
            calls, blocks = await self._stats.purge(days)
            await event.reply(i18n.t("GovReport.purge_done", calls=calls, blocks=blocks, days=days))
