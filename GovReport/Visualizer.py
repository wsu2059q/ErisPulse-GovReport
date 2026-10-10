import asyncio
from typing import Optional

PALETTES = {
    "light": {
        "page": "#f4f6f9", "card": "#ffffff", "ink": "#2b3440", "sub": "#7d8a99",
        "accent": "#4a7fb5", "accent2": "#5aa27b", "warn": "#c0804a", "err": "#bf6a6a",
        "accent_soft": "#e3edf7", "border": "#dfe6ee", "chipbg": "#f0f4f9", "codebg": "#eef2f7",
    },
    "dark": {
        "page": "#171b21", "card": "#20262e", "ink": "#e6ebf1", "sub": "#93a1b0",
        "accent": "#7aa9d9", "accent2": "#7fc29a", "warn": "#d3a569", "err": "#d98a8a",
        "accent_soft": "rgba(122,169,217,0.14)", "border": "#2c343e",
        "chipbg": "rgba(122,169,217,0.08)", "codebg": "#262d36",
    },
}

_FONTS = '"Noto Sans SC", "Roboto", "PingFang SC", "Microsoft YaHei", sans-serif'
_FONTS_MONO = '"JetBrains Mono", "Cascadia Code", Consolas, ui-monospace, monospace'

_CSS_TPL = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: __FONTS__; color: __INK__; -webkit-font-smoothing: antialiased; }
.page { background: __PAGE__; padding: 24px; }
.card { background: __CARD__; border: 1px solid __BORDER__; border-radius: 16px; overflow: hidden; }
.head { display: flex; justify-content: space-between; align-items: center; padding: 18px 24px; border-bottom: 1px solid __BORDER__; }
.title { font-size: 19px; font-weight: 700; letter-spacing: 0.5px; }
.subtitle { font-size: 12.5px; color: __SUB__; margin-top: 3px; }
.body { padding: 18px 24px 22px; }
.nums { display: flex; gap: 12px; }
.num { flex: 1; background: __CODEBG__; border-radius: 12px; padding: 14px 16px; text-align: center; }
.num .label { font-size: 12px; color: __SUB__; }
.num .value { font-size: 26px; font-weight: 700; color: __ACCENT__; margin-top: 4px; }
.num.ok .value { color: __ACCENT2__; }
.num.bad .value { color: __ERR__; }
.num.warn .value { color: __WARN__; }
.section { margin-top: 18px; }
.section-title { font-size: 12.5px; color: __SUB__; font-weight: 600; letter-spacing: 1px; margin-bottom: 8px; text-transform: uppercase; }
.bars { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { flex: 0 0 170px; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: __FONTMONO__; }
.bar-track { flex: 1; height: 16px; background: __CODEBG__; border-radius: 9999px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 9999px; background: __ACCENT__; }
.bar-value { flex: 0 0 52px; text-align: right; font-size: 12.5px; color: __SUB__; font-family: __FONTMONO__; }
.kv-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.kv { background: __CHIPBG__; border: 1px solid __BORDER__; border-radius: 8px; padding: 6px 12px; font-size: 13px; }
.kv b { color: __ACCENT__; font-weight: 600; }
.row { padding: 10px 12px; border-radius: 10px; margin-bottom: 6px; background: __CHIPBG__; border: 1px solid __BORDER__; }
.row:last-child { margin-bottom: 0; }
.row-main { display: flex; align-items: center; gap: 10px; }
.row-name { font-family: __FONTMONO__; font-size: 13px; background: __CODEBG__; border-radius: 6px; padding: 3px 8px; }
.row-dim { font-size: 12px; color: __SUB__; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-count { font-size: 15px; font-weight: 700; color: __ACCENT__; font-family: __FONTMONO__; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.chip { font-size: 11.5px; background: __ACCENT_SOFT__; color: __ACCENT__; border-radius: 9999px; padding: 2px 10px; }
.chip.warn { color: __WARN__; }
.chip.err { color: __ERR__; }
.empty { text-align: center; color: __SUB__; font-size: 13px; padding: 18px 0; }
.foot { padding: 12px 24px; border-top: 1px solid __BORDER__; font-size: 11.5px; color: __SUB__; display: flex; justify-content: space-between; }
"""


def _esc(text) -> str:
    import html

    return html.escape(str(text))


class CardVisualizer:

    CARD_WIDTH = 780

    def __init__(self, sdk, logger):
        self.sdk = sdk
        self.logger = logger
        self._takumi_inst = None

    @property
    def takumi(self):
        if self._takumi_inst is None:
            inst = None
            try:
                inst = self.sdk.module.get("Takumi")
            except Exception:
                inst = None
            if inst is None:
                inst = getattr(self.sdk, "Takumi", None)
            self._takumi_inst = inst
        return self._takumi_inst

    def resolve_palette(self, theme: str) -> dict:
        import datetime

        if theme in PALETTES:
            mode = theme
        else:
            hour = datetime.datetime.now().hour
            mode = "dark" if (hour >= 19 or hour < 7) else "light"
        return dict(PALETTES[mode])

    def _css(self, palette: dict) -> str:
        css = _CSS_TPL.replace("__FONTS__", _FONTS).replace("__FONTMONO__", _FONTS_MONO)
        for key, value in palette.items():
            css = css.replace(f"__{key.upper()}__", value)
        return css

    async def render(self, body_html: str, theme: str = "auto") -> Optional[bytes]:
        takumi = self.takumi
        if takumi is None or not hasattr(takumi, "render_html"):
            self.logger.debug("Takumi 不可用，跳过渲染")
            return None
        try:
            result = takumi.render_html(
                f"<div class='page'>{body_html}</div>",
                stylesheets=[self._css(self.resolve_palette(theme))],
                width=self.CARD_WIDTH,
                height=None,
                lang="zh-CN",
            )
            if asyncio.iscoroutine(result):
                result = await result
            return result if isinstance(result, (bytes, bytearray)) else None
        except Exception as e:
            self.logger.warning(f"渲染卡片失败: {e}")
            return None

    def head(self, title: str, subtitle: str) -> str:
        return (
            f"<div class='head'><div><div class='title'>{_esc(title)}</div>"
            f"<div class='subtitle'>{_esc(subtitle)}</div></div></div>"
        )

    def foot(self, left: str, right: str) -> str:
        return f"<div class='foot'><span>{_esc(left)}</span><span>{_esc(right)}</span></div>"

    @staticmethod
    def nums(items) -> str:
        cells = "".join(
            f"<div class='num {cls}'><div class='label'>{_esc(label)}</div>"
            f"<div class='value'>{_esc(value)}</div></div>"
            for label, value, cls in items
        )
        return f"<div class='nums'>{cells}</div>"

    @staticmethod
    def bars(pairs, color: str = "accent") -> str:
        if not pairs:
            return "<div class='empty'>无数据</div>"
        top = max(v for _, v in pairs) or 1
        fill = f"__ACCENT__" if color == "accent" else f"__{color.upper()}__"
        rows = "".join(
            f"<div class='bar-row'><span class='bar-label'>{_esc(k)}</span>"
            f"<div class='bar-track'><div class='bar-fill' style='width:{max(3, round(v / top * 100))}%;background:{fill}'></div></div>"
            f"<span class='bar-value'>{_esc(v)}</span></div>"
            for k, v in pairs
        )
        return f"<div class='bars'>{rows}</div>"

    @staticmethod
    def kv_section(title: str, pairs) -> str:
        chips = "".join(f"<div class='kv'>{_esc(k)} <b>{_esc(v)}</b></div>" for k, v in pairs)
        return (
            f"<div class='section'><div class='section-title'>{_esc(title)}</div>"
            f"<div class='kv-grid'>{chips}</div></div>"
        )

    @staticmethod
    def bar_section(title: str, pairs, color: str = "accent") -> str:
        return (
            f"<div class='section'><div class='section-title'>{_esc(title)}</div>"
            f"{CardVisualizer.bars(pairs, color)}</div>"
        )

    @staticmethod
    def count_row(name: str, right: str, dim: str = "", chips: str = "") -> str:
        return (
            f"<div class='row'><div class='row-main'>"
            f"<span class='row-name'>{_esc(name)}</span>"
            f"<span class='row-dim'>{_esc(dim)}</span>"
            f"<span class='row-count'>{_esc(right)}</span></div>{chips}</div>"
        )

    @staticmethod
    def chips(items, cls: str = "") -> str:
        if not items:
            return ""
        rendered = "".join(
            f"<span class='chip {cls}'>{_esc(t)}</span>" for t in items
        )
        return f"<div class='chips'>{rendered}</div>"
