import asyncio
from typing import Optional

PALETTES = {
    "editorial": {
        "_tpl": "editorial",
        "page": "#F9F8F6", "card": "#F9F8F6", "ink": "#1C1C1C", "sub": "rgba(28,28,28,0.4)",
        "accent": "#1C1C1C", "accent2": "rgba(28,28,28,0.6)", "warn": "rgba(28,28,28,0.6)",
        "err": "#1C1C1C", "accent_soft": "rgba(28,28,28,0.03)", "border": "rgba(28,28,28,0.1)",
        "chipbg": "transparent", "codebg": "rgba(28,28,28,0.03)",
    },
    "doodle": {
        "_tpl": "doodle",
        "page": "#fffef5", "card": "#fffef5", "ink": "#2c2c2c", "sub": "rgba(44,44,44,0.55)",
        "accent": "#ff6b6b", "accent2": "#4ecdc4", "warn": "#d9a800", "err": "#ff6b6b",
        "accent_soft": "rgba(255,217,61,0.4)", "border": "#2c2c2c",
        "chipbg": "#f8f7f0", "codebg": "#f8f7f0",
    },
}

_FONTS = '"Noto Sans SC", "Roboto", "PingFang SC", "Microsoft YaHei", sans-serif'
_FONTS_SERIF = 'Georgia, "Noto Serif SC", "Source Han Serif SC", "SimSun", serif'
_FONTS_MONO = '"JetBrains Mono", "Cascadia Code", Consolas, ui-monospace, monospace'



def _esc(text) -> str:
    import html

    return html.escape(str(text))


_CSS_EDITORIAL_TPL = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: __FONTS__; color: __INK__; -webkit-font-smoothing: antialiased; }
.page { background: __PAGE__; padding: 32px; }
.card { background: __CARD__; border: 1px solid __BORDER__; border-radius: 0; }
.head { padding: 24px 28px 20px; border-bottom: 1px solid __BORDER__; }
.title { font-family: __FONTSERIF__; font-size: 24px; font-weight: 400; letter-spacing: -0.5px; }
.subtitle { font-size: 11px; color: __SUB__; margin-top: 6px; letter-spacing: 0.12em; text-transform: uppercase; }
.body { padding: 24px 28px 28px; }
.nums { display: flex; border-bottom: 1px solid __BORDER__; }
.num { flex: 1; text-align: center; padding: 18px 12px 16px; }
.num + .num { border-left: 1px solid __BORDER__; }
.num .label { font-size: 10px; color: __SUB__; letter-spacing: 0.12em; text-transform: uppercase; }
.num .value { font-family: __FONTSERIF__; font-size: 30px; font-weight: 400; margin-top: 8px; }
.num.ok .value { color: __INK__; }
.num.bad .value { color: __SUB__; }
.num.warn .value { color: __WARN__; }
.section { margin-top: 24px; }
.section-title { font-size: 10px; color: __SUB__; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px; }
.kv-grid { display: flex; flex-wrap: wrap; gap: 0; }
.kv { border: 1px solid __BORDER__; border-radius: 0; padding: 6px 14px; font-size: 12px; }
.kv + .kv { margin-left: -1px; }
.kv b { font-weight: 600; }
.bars { display: flex; flex-direction: column; gap: 0; }
.bar-row { display: flex; align-items: baseline; gap: 12px; padding: 8px 0; border-bottom: 1px solid __BORDER__; }
.bar-row:last-child { border-bottom: none; }
.bar-label { flex: 0 0 170px; font-size: 12px; font-family: __FONTMONO__; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bar-track { flex: 1; height: 10px; border: 1px solid __BORDER__; }
.bar-fill { height: 100%; background: __INK__; }
.bar-value { flex: 0 0 52px; text-align: right; font-size: 12px; color: __SUB__; font-family: __FONTMONO__; }
.row { padding: 10px 0; margin-bottom: 0; border-bottom: 1px solid __BORDER__; background: transparent; border-radius: 0; }
.row:last-child { border-bottom: none; }
.row-main { display: flex; align-items: baseline; gap: 12px; }
.row-name { font-family: __FONTSERIF__; font-size: 15px; background: transparent; border-radius: 0; padding: 0; }
.row-dim { font-size: 12px; color: __SUB__; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-count { font-family: __FONTSERIF__; font-size: 15px; }
.row-count.ok { color: __INK__; }
.row-count.miss { color: __SUB__; }
.cid { font-family: __FONTMONO__; font-size: 12px; background: transparent; border: 0; border-radius: 0; padding: 0; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.badge {
    display: inline-block; padding: 2px 10px; font-size: 10px; font-weight: 400;
    color: #F9F8F6; background: #1C1C1C; border-radius: 0;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.dim { font-size: 12px; color: __SUB__; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
.chip {
    font-size: 10px; color: __SUB__; border: 1px solid __BORDER__; border-radius: 0;
    padding: 2px 10px; letter-spacing: 0.1em; text-transform: uppercase; background: transparent;
}
.chip.warn { color: __WARN__; }
.chip.err { color: __INK__; border-color: rgba(28,28,28,0.4); }
.empty { text-align: center; color: __SUB__; font-size: 12px; padding: 24px 0; letter-spacing: 0.2em; }
.pre { font-family: __FONTMONO__; font-size: 15px; line-height: 1.5; white-space: pre; padding: 20px 24px; border-top: 1px solid __BORDER__; border-bottom: 1px solid __BORDER__; }
.foot { padding: 14px 28px; border-top: 1px solid __BORDER__; font-size: 10px; color: __SUB__; display: flex; justify-content: space-between; letter-spacing: 0.12em; text-transform: uppercase; }
"""

_CSS_DOODLE_TPL = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: __FONTS__; color: __INK__; -webkit-font-smoothing: antialiased; }
.page {
    background: __PAGE__;
    background-image:
        repeating-linear-gradient(to bottom, transparent 0px, transparent 31px, rgba(110,140,200,0.20) 31px, rgba(110,140,200,0.20) 32px),
        linear-gradient(to right, transparent 42px, rgba(255,107,107,0.35) 42px, rgba(255,107,107,0.35) 44px, transparent 44px);
    padding: 36px 36px 38px 64px;
}
.card {
    position: relative; background: __CARD__;
    border: 2px dashed __BORDER__; border-radius: 4px;
    box-shadow: 5px 5px 0 __ACCENT2__; overflow: visible;
}
.card::before {
    content: ""; position: absolute; top: -11px; left: 50%;
    width: 120px; height: 22px; background: rgba(255,217,61,0.5);
    transform: translateX(-50%) rotate(-2deg); border-radius: 2px;
}
.head { padding: 22px 26px 16px; border-bottom: 2px dashed rgba(44,44,44,0.35); }
.title { font-size: 21px; font-weight: 800; letter-spacing: 0.5px; transform: rotate(-0.6deg); }
.subtitle { font-size: 12.5px; color: __SUB__; margin-top: 4px; }
.body { padding: 18px 26px 24px; }
.nums { display: flex; gap: 12px; }
.num {
    flex: 1; background: __CODEBG__; border: 2px dashed rgba(44,44,44,0.35);
    border-radius: 4px; padding: 12px 12px; text-align: center;
}
.num .label { font-size: 12px; color: __SUB__; }
.num .value { font-size: 26px; font-weight: 800; color: __ACCENT__; margin-top: 4px; }
.num.ok .value { color: #4ecdc4; }
.num.bad .value { color: __ERR__; }
.num.warn .value { color: __WARN__; }
.section { margin-top: 18px; }
.section-title { font-size: 13px; color: __SUB__; font-weight: 700; margin-bottom: 8px; transform: rotate(-0.3deg); }
.kv-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.kv {
    background: __CHIPBG__; border: 1.5px dashed rgba(44,44,44,0.4);
    border-radius: 4px; padding: 5px 12px; font-size: 13px;
}
.kv b { color: __ACCENT__; font-weight: 700; }
.bars { display: flex; flex-direction: column; gap: 8px; }
.bar-row { display: flex; align-items: center; gap: 10px; }
.bar-label { flex: 0 0 170px; font-size: 12.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: __FONTMONO__; }
.bar-track { flex: 1; height: 16px; border: 1.5px dashed rgba(44,44,44,0.4); border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; background: __INK__; }
.bar-value { flex: 0 0 52px; text-align: right; font-size: 12.5px; color: __SUB__; font-family: __FONTMONO__; }
.row {
    padding: 10px 12px; border-radius: 4px; margin-bottom: 6px;
    background: __CHIPBG__; border: 1.5px dashed rgba(44,44,44,0.4);
}
.row:last-child { margin-bottom: 0; }
.row-main { display: flex; align-items: center; gap: 10px; }
.row-name { font-size: 13px; font-weight: 700; background: __CODEBG__; border: 1.5px dashed rgba(44,44,44,0.35); border-radius: 4px; padding: 3px 8px; }
.row-dim { font-size: 12px; color: __SUB__; flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-count { font-size: 15px; font-weight: 800; color: __ACCENT__; }
.row-count.ok { color: #4ecdc4; }
.row-count.miss { color: __WARN__; }
.cid { font-family: __FONTMONO__; font-size: 12.5px; background: __CODEBG__; border: 1.5px dashed rgba(44,44,44,0.35); border-radius: 4px; padding: 3px 8px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.badge {
    display: inline-block; padding: 3px 10px; font-size: 11px; font-weight: 700;
    color: #fffef5; border: 1.5px dashed #2c2c2c; border-radius: 4px;
    transform: rotate(1deg);
}
.dim { font-size: 12px; color: __SUB__; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.chip {
    font-size: 11.5px; background: __ACCENT_SOFT__; color: __INK__;
    border: 1.5px dashed rgba(44,44,44,0.4); border-radius: 4px; padding: 2px 10px;
}
.chip.warn { background: rgba(255,217,61,0.4); }
.chip.err { background: rgba(255,107,107,0.25); }
.empty { text-align: center; color: __SUB__; font-size: 13px; padding: 18px 0; }
.pre { font-family: __FONTMONO__; font-size: 15px; line-height: 1.5; white-space: pre; background: __CODEBG__; border: 1.5px dashed rgba(44,44,44,0.4); border-radius: 4px; padding: 14px 18px; }
.foot { padding: 12px 26px; border-top: 2px dashed rgba(44,44,44,0.35); font-size: 11.5px; color: __SUB__; display: flex; justify-content: space-between; }
"""

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
        palette = PALETTES.get(theme, PALETTES["doodle"])
        return dict(palette)


    def _css(self, palette: dict) -> str:
        tpl = _CSS_DOODLE_TPL if palette.get("_tpl") == "doodle" else _CSS_EDITORIAL_TPL
        css = tpl.replace("__FONTS__", _FONTS).replace("__FONTMONO__", _FONTS_MONO).replace("__FONTSERIF__", _FONTS_SERIF)
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
