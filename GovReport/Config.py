from dataclasses import dataclass, field

from ErisPulse.Core.Bases import BaseConfig


@dataclass
class GovReportConfig(BaseConfig):

    enabled: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "GovReport.enabled", "default": "是否启用模块"},
            "ui": {"widget": "switch", "group": "basic", "order": 1},
        },
    )
    collect_command_calls: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "GovReport.collect_command_calls", "default": "采集命令执行记录（command.executed）"},
            "ui": {"widget": "switch", "group": "collect", "order": 2},
        },
    )
    collect_blocked: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "GovReport.collect_blocked", "default": "采集事件拦截记录（中间件否决 / 作用域拦截）"},
            "ui": {"widget": "switch", "group": "collect", "order": 3},
        },
    )
    retention_days: int = field(
        default=30,
        metadata={
            "description": {"i18n": "GovReport.retention_days", "default": "记录保留天数（0 永久保留，启动与每日清理）"},
            "ui": {"widget": "number", "group": "collect", "order": 4},
        },
    )
    top_n: int = field(
        default=10,
        metadata={
            "description": {"i18n": "GovReport.top_n", "default": "统计报表单次展示的最大条目数"},
            "ui": {"widget": "number", "group": "report", "order": 5},
        },
    )
    render_card: bool = field(
        default=True,
        metadata={
            "description": {"i18n": "GovReport.render_card", "default": "报表用 Takumi 渲染为卡片（不可用时降级文本）"},
            "ui": {"widget": "switch", "group": "render", "order": 6},
        },
    )
    theme: str = field(
        default="doodle",
        metadata={
            "description": {"i18n": "GovReport.theme", "default": "卡片风格 (doodle/editorial)"},
            "ui": {
                "widget": "select",
                "options": ["doodle", "editorial"],
                "group": "render",
                "order": 7,
            },
        },
    )
