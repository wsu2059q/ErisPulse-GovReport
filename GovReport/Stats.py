import time
from typing import Any, Optional

from ErisPulse import i18n

from .Models import BlockEvent, CommandCall

USAGE_KEY_PREFIX = "erispulse.usage"
SEP = "\x00"


def parse_window(window: str) -> Optional[float]:
    from ErisPulse.Core.Event import command_args

    try:
        seconds = command_args.parse_duration(window)
    except Exception:
        return None
    if seconds is None or seconds <= 0:
        return None
    return float(seconds)


def _fmt_window(window: str) -> str:
    return window


class GovStatsService:

    def __init__(self, logger):
        self._logger = logger

    async def _command_window(self, window_secs: float) -> list:
        cutoff = time.time() - window_secs
        return await CommandCall.where(CommandCall.ts >= cutoff).all()

    @staticmethod
    def _top(rows: list, key: str, top_n: int) -> list:
        counter: dict[str, int] = {}
        for r in rows:
            k = getattr(r, key) or "-"
            counter[k] = counter.get(k, 0) + 1
        return sorted(counter.items(), key=lambda kv: -kv[1])[:top_n]

    async def _usage_entries(self) -> dict:
        from ErisPulse import sdk

        storage = sdk.storage
        try:
            root = await storage.aget("erispulse")
        except Exception as e:
            self._logger.warning(f"读取配额根键失败: {e}")
            return {}
        if not isinstance(root, dict):
            return {}
        return {
            k: v for k, v in root.items()
            if isinstance(k, str) and k.startswith("usage" + SEP)
        }

    async def command_stats_card(self, window_text: str, top_n: int, viz) -> str:
        import datetime

        rows = await self._command_window(parse_window(window_text) or 0)
        total = len(rows)
        if not total:
            body = "<div class='empty'>窗口内没有命令记录</div>"
        else:
            ok = sum(1 for r in rows if r.success)
            dep = sum(1 for r in rows if r.error == "deprecated")
            body = viz.nums([
                ("总调用", total, ""),
                ("成功", ok, "ok"),
                ("失败", total - ok, "bad"),
                ("废弃使用", dep, "warn"),
            ])
            body += viz.bar_section("命令 Top", self._top(rows, "command", top_n))
            body += viz.bar_section("用户 Top", self._top(rows, "user_id", top_n), color="accent2")
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head("命令执行统计", f"窗口 {window_text} · 共 {total} 次调用")
            + f"<div class='body'>{body}</div>"
            + viz.foot(f"GovReport · {stamp}", f"Top {top_n}")
        )

    async def blocked_stats_card(self, window_text: str, top_n: int, viz) -> str:
        import datetime

        cutoff = time.time() - (parse_window(window_text) or 0)
        rows = await BlockEvent.where(BlockEvent.ts >= cutoff).all()
        total = len(rows)
        if not total:
            body = "<div class='empty'>窗口内没有拦截记录</div>"
        else:
            mw = sum(1 for r in rows if r.source == "middleware")
            body = viz.nums([
                ("总拦截", total, ""),
                ("中间件否决", mw, "warn"),
                ("作用域拦截", total - mw, ""),
            ])
            by_name: dict[str, int] = {}
            for r in rows:
                if r.source == "middleware":
                    name = r.middleware or "-"
                else:
                    name = f"{r.dimension or '-'}:{r.module or '-'}"
                by_name[name] = by_name.get(name, 0) + 1
            pairs = sorted(by_name.items(), key=lambda kv: -kv[1])[:top_n]
            body += viz.bar_section("拦截来源", pairs, color="err")
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head("事件拦截统计", f"窗口 {window_text} · 共 {total} 次")
            + f"<div class='body'>{body}</div>"
            + viz.foot(f"GovReport · {stamp}", "middleware / scope")
        )

    async def usage_report_card(self, viz) -> str:
        import datetime

        entries = await self._usage_entries()
        if not entries:
            body = "<div class='empty'>没有配额消耗记录</div>"
        else:
            limits = self._usage_limits()
            rows = []
            for key in sorted(entries, key=lambda k: -entries[k]):
                parts = key[len("usage" + SEP):].split(SEP)
                main_name = parts[0]
                scope = parts[1] if len(parts) > 1 else "?"
                period = parts[2] if len(parts) > 2 else "?"
                limit, unit = limits.get(main_name, (None, ""))
                right = f"{entries[key]}/{limit}" if limit is not None else str(entries[key])
                chips = viz.chips([f"period {period}", f"scope {scope}"])
                rows.append(viz.count_row(main_name, right, unit or "", chips))
            body = "".join(rows)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head("配额消耗", f"活跃键 {len(entries)} 个")
            + f"<div class='body'>{body}</div>"
            + viz.foot(f"GovReport · {stamp}", "usage_limit")
        )

    def governance_list_card(self, name_filter, viz) -> str:
        import datetime

        from ErisPulse.Core.Event import command

        registry = command.get_commands()
        rows = []
        for cmd_name, info in sorted(registry.items()):
            if cmd_name != info.get("main_name"):
                continue
            if name_filter and name_filter not in cmd_name:
                continue
            chips = []
            cooldown = info.get("cooldown_seconds")
            if cooldown:
                chips.append(f"cooldown {cooldown:g}s · {info.get('cooldown_key') or 'user'}")
            rate = info.get("rate_limit_spec")
            if rate:
                chips.append(f"rate {rate[0]}/{rate[1]:g}s · {info.get('rate_limit_key') or 'user'}")
            usage = info.get("usage_spec")
            if usage:
                chips.append(f"usage {usage[0]}/{usage[1]} · {info.get('usage_limit_key') or 'user'}")
            deprecated = info.get("deprecated")
            if deprecated:
                chips.append(f"deprecated{'(reject)' if info.get('deprecated_reject') else ''}: {deprecated}")
            if chips:
                rows.append(viz.count_row(
                    cmd_name, "", "",
                    viz.chips(chips, cls="warn" if deprecated else ""),
                ))
        body = "".join(rows) if rows else "<div class='empty'>没有任何命令声明治理规则</div>"
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return (
            viz.head("治理声明清单", f"{len(rows)} 个命令声明了治理规则")
            + f"<div class='body'>{body}</div>"
            + viz.foot(f"GovReport · {stamp}", "cooldown / rate / usage / deprecated")
        )

    async def command_stats(self, window_secs: float, window_text: str, top_n: int) -> str:
        cutoff = time.time() - window_secs
        rows = await CommandCall.where(CommandCall.ts >= cutoff).all()
        if not rows:
            return i18n.t("GovReport.stats_empty", window=_fmt_window(window_text))
        total = len(rows)
        ok = sum(1 for r in rows if r.success)
        dep = sum(1 for r in rows if r.error == "deprecated")
        lines = [i18n.t(
            "GovReport.stats_header",
            window=_fmt_window(window_text), total=total, ok=ok, failed=total - ok, dep=dep,
        )]
        by_cmd: dict[str, int] = {}
        for r in rows:
            by_cmd[r.command] = by_cmd.get(r.command, 0) + 1
        for cmd, count in sorted(by_cmd.items(), key=lambda kv: -kv[1])[:top_n]:
            lines.append(f"{cmd}: {count}")
        return "\n".join(lines)

    async def user_stats(self, user_id: str, window_secs: float, window_text: str, top_n: int) -> str:
        cutoff = time.time() - window_secs
        rows = await CommandCall.where(
            (CommandCall.ts >= cutoff) & (CommandCall.user_id == user_id)
        ).all()
        if not rows:
            return i18n.t("GovReport.user_empty", user=user_id, window=_fmt_window(window_text))
        total = len(rows)
        ok = sum(1 for r in rows if r.success)
        lines = [i18n.t(
            "GovReport.user_header",
            user=user_id, window=_fmt_window(window_text), total=total, ok=ok, failed=total - ok,
        )]
        by_cmd: dict[str, int] = {}
        for r in rows:
            by_cmd[r.command] = by_cmd.get(r.command, 0) + 1
        for cmd, count in sorted(by_cmd.items(), key=lambda kv: -kv[1])[:top_n]:
            lines.append(f"{cmd}: {count}")
        return "\n".join(lines)

    async def blocked_stats(self, window_secs: float, window_text: str, top_n: int) -> str:
        cutoff = time.time() - window_secs
        rows = await BlockEvent.where(BlockEvent.ts >= cutoff).all()
        if not rows:
            return i18n.t("GovReport.blocked_empty", window=_fmt_window(window_text))
        lines = [i18n.t("GovReport.blocked_header", window=_fmt_window(window_text), total=len(rows))]
        by_source: dict[str, int] = {}
        by_name: dict[str, int] = {}
        for r in rows:
            by_source[r.source] = by_source.get(r.source, 0) + 1
            if r.source == "middleware":
                name = f"middleware:{r.middleware or '-'}"
            else:
                name = f"scope:{r.dimension or '-'}:{r.module or '-'}"
            by_name[name] = by_name.get(name, 0) + 1
        rendered = " ".join(f"{k}={v}" for k, v in sorted(by_source.items()))
        lines.append(f"by_source: {rendered}")
        for name, count in sorted(by_name.items(), key=lambda kv: -kv[1])[:top_n]:
            lines.append(f"{name}: {count}")
        return "\n".join(lines)

    async def usage_report(self) -> str:
        from ErisPulse import sdk

        storage = sdk.storage
        root_key = USAGE_KEY_PREFIX.split(".")[0]
        nested_prefix = USAGE_KEY_PREFIX.split(".", 1)[1] + SEP
        try:
            root = await storage.aget(root_key)
        except Exception as e:
            self._logger.warning(f"读取配额根键失败: {e}")
            root = None
        entries: dict[str, Any] = {}
        if isinstance(root, dict):
            entries = {
                k: v for k, v in root.items()
                if isinstance(k, str) and k.startswith(nested_prefix)
            }
        if not entries:
            return i18n.t("GovReport.usage_empty")

        limits = self._usage_limits()
        lines = [i18n.t("GovReport.usage_header", count=len(entries))]
        for key in sorted(entries):
            parts = key[len(nested_prefix):].split(SEP)
            main_name = parts[0] if parts else "?"
            scope = parts[1] if len(parts) > 1 else "?"
            period = parts[2] if len(parts) > 2 else "?"
            used = entries[key]
            limit, unit = limits.get(main_name, (None, ""))
            limit_text = f"/{limit}({unit})" if limit is not None else ""
            lines.append(f"{main_name}: {used}{limit_text} period={period} scope={scope}")
        return "\n".join(lines)

    @staticmethod
    def _usage_limits() -> dict[str, tuple[Any, str]]:
        from ErisPulse.Core.Event import command

        limits: dict[str, tuple[Any, str]] = {}
        try:
            registry = command.get_commands()
        except Exception:
            return limits
        for info in registry.values():
            spec = info.get("usage_spec")
            main_name = info.get("main_name")
            if spec and main_name:
                limits[main_name] = (spec[0], spec[1])
        return limits

    def governance_list(self, name_filter: Optional[str] = None) -> str:
        from ErisPulse.Core.Event import command

        registry = command.get_commands()
        lines = []
        for cmd_name, info in sorted(registry.items()):
            if cmd_name != info.get("main_name"):
                continue
            if name_filter and name_filter not in cmd_name:
                continue
            parts = []
            cooldown = info.get("cooldown_seconds")
            if cooldown:
                parts.append(f"cooldown={cooldown:g}s({info.get('cooldown_key') or 'user'})")
            rate = info.get("rate_limit_spec")
            if rate:
                parts.append(f"rate={rate[0]}/{rate[1]:g}s({info.get('rate_limit_key') or 'user'})")
            usage = info.get("usage_spec")
            if usage:
                parts.append(f"usage={usage[0]}/{usage[1]}({info.get('usage_limit_key') or 'user'})")
            deprecated = info.get("deprecated")
            if deprecated:
                reject = "reject" if info.get("deprecated_reject") else "notice"
                parts.append(f"deprecated[{reject}]={deprecated}")
            if parts:
                lines.append(f"{cmd_name}: {' '.join(parts)}")
        if not lines:
            return i18n.t("GovReport.gov_list_empty")
        return "\n".join([i18n.t("GovReport.gov_list_header", count=len(lines))] + lines)

    async def purge(self, days: int) -> tuple[int, int]:
        cutoff = time.time() - days * 86400
        calls = await CommandCall.delete_all(CommandCall.ts < cutoff)
        blocks = await BlockEvent.delete_all(BlockEvent.ts < cutoff)
        return calls, blocks

    async def purge_expired(self, retention_days: int) -> None:
        if retention_days <= 0:
            return
        calls, blocks = await self.purge(retention_days)
        if calls or blocks:
            self._logger.info(f"清理过期记录: 命令 {calls} 条, 拦截 {blocks} 条")
