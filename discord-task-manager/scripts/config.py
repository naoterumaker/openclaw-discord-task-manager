"""Discord Task Manager - 共通設定"""
import json, os

def get_token():
    path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(path) as f:
        d = json.load(f)
    return d["channels"]["discord"]["token"]

FORUM_CHANNEL_ID  = "1475147089871769643"  # 🤖-teru_masterタスク
TASK_LEADER_CH_ID = "1475156472072503377"  # タスクリーダーチャンネル
GUILD_ID          = "1474320833269993475"

TAGS = {
    "🔴高":    "1475171629565743281",
    "🟡中":    "1475171629565743282",
    "🟢低":    "1475171629565743283",
    "📚ナレッジ": "1475171629565743284",
    "完了":    "1475171629591167098",
    "⏸ブロック中": "1475171629591167099",
    "⏩実行可":  "1475263174667276360",  # cronウォッチャーが自律実行するタスク
}

PRIORITY_TAG = {"高": "🔴高", "中": "🟡中", "低": "🟢低"}

API_BASE = "https://discord.com/api/v10"
HEADERS_TEMPLATE = {
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (https://openclaw.ai, 1.0)",
}

def headers():
    h = dict(HEADERS_TEMPLATE)
    h["Authorization"] = f"Bot {get_token()}"
    return h
