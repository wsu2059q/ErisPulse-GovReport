from ErisPulse.Core.Bases import BaseI18n, I18nKey


class GovReportI18n(BaseI18n):

    enabled: I18nKey = I18nKey(
        default="Enable module",
        zh_CN="是否启用模块",
        zh_TW="是否啟用模組",
        en="Enable module",
        ja="モジュールを有効化",
        ru="Включить модуль",
    )
    collect_command_calls: I18nKey = I18nKey(
        default="Collect command execution records",
        zh_CN="采集命令执行记录（command.executed）",
        zh_TW="採集命令執行記錄（command.executed）",
        en="Collect command execution records",
        ja="コマンド実行記録を収集",
        ru="Собирать записи выполнения команд",
    )
    collect_blocked: I18nKey = I18nKey(
        default="Collect blocked event records (middleware veto / scope)",
        zh_CN="采集事件拦截记录（中间件否决 / 作用域拦截）",
        zh_TW="採集事件攔截記錄（中介軟體否決 / 作用域攔截）",
        en="Collect blocked event records (middleware veto / scope)",
        ja="ブロック記録を収集（ミドルウェア拒否 / スコープ）",
        ru="Собирать записи блокировки событий",
    )
    retention_days: I18nKey = I18nKey(
        default="Retention days (0 = keep forever)",
        zh_CN="记录保留天数（0 永久保留，启动与每日清理）",
        zh_TW="記錄保留天數（0 永久保留，啟動與每日清理）",
        en="Retention days (0 = keep forever)",
        ja="保持日数（0 で無期限保持）",
        ru="Срок хранения в днях (0 = бессрочно)",
    )
    top_n: I18nKey = I18nKey(
        default="Max entries shown in one report",
        zh_CN="统计报表单次展示的最大条目数",
        zh_TW="統計報表單次展示的最大條目數",
        en="Max entries shown in one report",
        ja="レポート1回の最大表示件数",
        ru="Максимум записей в одном отчёте",
    )
    render_card: I18nKey = I18nKey(
        default="Render reports as image cards via Takumi (fallback to text)",
        zh_CN="报表用 Takumi 渲染为卡片（不可用时降级文本）",
        zh_TW="報表用 Takumi 渲染為卡片（不可用時降級文本）",
        en="Render reports as image cards via Takumi (fallback to text)",
        ja="レポートを Takumi でカード画像化（不可時はテキスト）",
        ru="Рендер отчётов в карточки через Takumi (иначе текст)",
    )
    theme: I18nKey = I18nKey(
        default="Card color theme (auto = light/dark by time)",
        zh_CN="卡片配色 (auto=按时间自动切深浅色)",
        zh_TW="卡片配色 (auto=按時間自動切深淺色)",
        en="Card color theme (auto = light/dark by time)",
        ja="カード配色（auto=時間で自動切替）",
        ru="Тема карточек (auto = светлая/тёмная по времени)",
    )
    module_loaded: I18nKey = I18nKey(
        default="GovReport loaded: {event}",
        zh_CN="治理观测已加载: {event}",
        zh_TW="治理觀測已載入: {event}",
        en="GovReport loaded: {event}",
        ja="GovReport を読み込みました: {event}",
        ru="GovReport загружен: {event}",
    )
    module_unloaded: I18nKey = I18nKey(
        default="GovReport unloaded: {event}",
        zh_CN="治理观测已卸载: {event}",
        zh_TW="治理觀測已卸載: {event}",
        en="GovReport unloaded: {event}",
        ja="GovReport を解除しました: {event}",
        ru="GovReport выгружен: {event}",
    )
    stats_header: I18nKey = I18nKey(
        default="Command stats in last {window}: total {total}, success {ok}, failed {failed}, deprecated uses {dep}",
        zh_CN="近 {window} 命令统计：共 {total} 次，成功 {ok}，失败 {failed}，废弃命令使用 {dep} 次",
        zh_TW="近 {window} 命令統計：共 {total} 次，成功 {ok}，失敗 {failed}，廢棄命令使用 {dep} 次",
        en="Command stats in last {window}: total {total}, success {ok}, failed {failed}, deprecated uses {dep}",
        ja="直近 {window} のコマンド統計：合計 {total}、成功 {ok}、失敗 {failed}、非推奨使用 {dep}",
        ru="Статистика команд за {window}: всего {total}, успешно {ok}, ошибок {failed}, устаревших {dep}",
    )
    stats_empty: I18nKey = I18nKey(
        default="No command records in window {window}",
        zh_CN="窗口 {window} 内没有命令记录",
        zh_TW="視窗 {window} 內沒有命令記錄",
        en="No command records in window {window}",
        ja="期間 {window} にコマンド記録がありません",
        ru="За период {window} записей команд нет",
    )
    user_header: I18nKey = I18nKey(
        default="User {user} in last {window}: total {total}, success {ok}, failed {failed}",
        zh_CN="用户 {user} 近 {window}：共 {total} 次，成功 {ok}，失败 {failed}",
        zh_TW="用戶 {user} 近 {window}：共 {total} 次，成功 {ok}，失敗 {failed}",
        en="User {user} in last {window}: total {total}, success {ok}, failed {failed}",
        ja="ユーザー {user} 直近 {window}：合計 {total}、成功 {ok}、失敗 {failed}",
        ru="Пользователь {user} за {window}: всего {total}, успешно {ok}, ошибок {failed}",
    )
    user_empty: I18nKey = I18nKey(
        default="User {user} has no records in window {window}",
        zh_CN="用户 {user} 在窗口 {window} 内没有记录",
        zh_TW="用戶 {user} 在視窗 {window} 內沒有記錄",
        en="User {user} has no records in window {window}",
        ja="ユーザー {user} は期間 {window} に記録がありません",
        ru="У пользователя {user} нет записей за {window}",
    )
    blocked_header: I18nKey = I18nKey(
        default="Blocked events in last {window}: total {total}",
        zh_CN="近 {window} 拦截统计：共 {total} 次",
        zh_TW="近 {window} 攔截統計：共 {total} 次",
        en="Blocked events in last {window}: total {total}",
        ja="直近 {window} のブロック統計：合計 {total}",
        ru="Блокировки за {window}: всего {total}",
    )
    blocked_empty: I18nKey = I18nKey(
        default="No blocked events in window {window}",
        zh_CN="窗口 {window} 内没有拦截记录",
        zh_TW="視窗 {window} 內沒有攔截記錄",
        en="No blocked events in window {window}",
        ja="期間 {window} にブロック記録がありません",
        ru="За период {window} блокировок нет",
    )
    usage_header: I18nKey = I18nKey(
        default="Usage quota consumption ({count} active key(s)):",
        zh_CN="配额消耗（活跃键 {count} 个）：",
        zh_TW="配額消耗（活躍鍵 {count} 個）：",
        en="Usage quota consumption ({count} active key(s)):",
        ja="クォータ消費（アクティブキー {count} 件）：",
        ru="Потребление квот (активных ключей: {count}):",
    )
    usage_empty: I18nKey = I18nKey(
        default="No usage quota records",
        zh_CN="没有配额消耗记录",
        zh_TW="沒有配額消耗記錄",
        en="No usage quota records",
        ja="クォータ消費記録がありません",
        ru="Нет записей потребления квот",
    )
    gov_list_empty: I18nKey = I18nKey(
        default="No command has governance declarations",
        zh_CN="没有任何命令声明治理规则",
        zh_TW="沒有任何命令聲明治理規則",
        en="No command has governance declarations",
        ja="治理宣言を持つコマンドはありません",
        ru="Нет команд с правилами управления",
    )
    gov_list_header: I18nKey = I18nKey(
        default="Governance declarations ({count} command(s)):",
        zh_CN="治理声明清单（{count} 个命令）：",
        zh_TW="治理聲明清單（{count} 個命令）：",
        en="Governance declarations ({count} command(s)):",
        ja="治理宣言一覧（{count} 件）：",
        ru="Объявления управления ({count} команд):",
    )
    purge_done: I18nKey = I18nKey(
        default="Purged {calls} call record(s) and {blocks} block record(s) older than {days} day(s)",
        zh_CN="已清理 {days} 天前的记录：命令 {calls} 条，拦截 {blocks} 条",
        zh_TW="已清理 {days} 天前的記錄：命令 {calls} 條，攔截 {blocks} 條",
        en="Purged {calls} call record(s) and {blocks} block record(s) older than {days} day(s)",
        ja="{days} 日より前の記録を削除：コマンド {calls} 件、ブロック {blocks} 件",
        ru="Удалено записей старше {days} дн.: команд {calls}, блокировок {blocks}",
    )
    invalid_window: I18nKey = I18nKey(
        default="Invalid window: {window} (examples: 30m / 24h / 7d)",
        zh_CN="无效的时间窗口: {window}（示例: 30m / 24h / 7d）",
        zh_TW="無效的時間視窗: {window}（示例: 30m / 24h / 7d）",
        en="Invalid window: {window} (examples: 30m / 24h / 7d)",
        ja="無効な期間指定: {window}（例: 30m / 24h / 7d）",
        ru="Неверный период: {window} (примеры: 30m / 24h / 7d)",
    )
