#!/usr/bin/env python3
"""
朝のタスクサマリー（cron 8:00 AM から実行）
未完了タスク一覧 + 優先度別のおすすめをタスクリーダーChに投稿
"""
import sys, json, urllib.request, urllib.error, datetime
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *
from list_tasks import list_tasks

def post_message(channel_id, content):
    body = {"content": content}
    req = urllib.request.Request(
        f"{API_BASE}/channels/{channel_id}/messages",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def morning():
    tasks = list_tasks(as_json=False)
    if not isinstance(tasks, list):
        return

    today = datetime.date.today().strftime("%Y/%m/%d")
    jst_hour = datetime.datetime.now().hour

    high   = [t for t in tasks if t["priority"] == "🔴高"]
    mid    = [t for t in tasks if t["priority"] == "🟡中"]
    low    = [t for t in tasks if t["priority"] == "🟢低"]

    lines = [f"☀️ **おはようございます！ {today} のタスク確認**\n"]

    if not tasks:
        lines.append("📭 アクティブなタスクはありません。今日も頑張りましょう！")
    else:
        lines.append(f"📋 未完了タスク: **{len(tasks)}件**\n")

        if high:
            lines.append("🔴 **優先度: 高**")
            for t in high:
                lines.append(f"　• {t['title']} (<{t['url']}>)")
        if mid:
            lines.append("🟡 **優先度: 中**")
            for t in mid:
                lines.append(f"　• {t['title']} (<{t['url']}>)")
        if low:
            lines.append("🟢 **優先度: 低**")
            for t in low:
                lines.append(f"　• {t['title']} (<{t['url']}>)")

        # 今日のおすすめ
        today_picks = (high or mid or low)[:3]
        lines.append("\n💡 **今日着手おすすめ**")
        for t in today_picks:
            lines.append(f"　→ {t['priority']} {t['title']}")

    msg = "\n".join(lines)

    # タスクリーダーチャンネルに投稿
    result = post_message(TASK_LEADER_CH_ID, msg)
    print(f"✅ 朝のサマリー投稿完了 (message_id: {result['id']})")

if __name__ == "__main__":
    morning()
