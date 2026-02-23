#!/usr/bin/env python3
"""
夜の振り返りサマリー（cron 22:00 から実行）
残タスク一覧 + 明日の準備確認をタスクリーダーChに投稿
"""
import sys, json, urllib.request, urllib.error, datetime
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *
from list_tasks import list_tasks, list_done_tasks

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

def evening():
    tasks = list_tasks(as_json=False)
    done_tasks = list_done_tasks()
    if not isinstance(tasks, list):
        return

    today = datetime.date.today().strftime("%Y/%m/%d")

    high   = [t for t in tasks if t["priority"] == "🔴高"]
    mid    = [t for t in tasks if t["priority"] == "🟡中"]
    low    = [t for t in tasks if t["priority"] == "🟢低"]

    lines = [f"🌙 **お疲れ様でした！ {today} の振り返り**\n"]

    if not tasks:
        lines.append("🎉 未完了タスクはゼロ！完璧な一日でした！")
    else:
        lines.append(f"📋 残タスク: **{len(tasks)}件**\n")

        if high:
            lines.append("🔴 **明日最優先でやること**")
            for t in high:
                lines.append(f"　• {t['title']} (<{t['url']}>)")
        if mid:
            lines.append("🟡 **引き続き対応**")
            for t in mid:
                lines.append(f"　• {t['title']} (<{t['url']}>)")
        if low:
            lines.append("🟢 **余裕があれば**")
            for t in low:
                lines.append(f"　• {t['title']} (<{t['url']}>)")

        lines.append("\n💡 **明日の準備**")
        lines.append(f"　→ 🔴高のタスクから着手: {high[0]['title']}" if high else "　→ 🟡中のタスクから: " + (mid[0]['title'] if mid else "ゆっくり決めて"))

    # 完了タスク（振り返り）
    if done_tasks:
        lines.append(f"\n✅ **完了済みタスク ({len(done_tasks)}件)**")
        for t in done_tasks:
            lines.append(f"　• {t['title']} (<{t['url']}>)")

    msg = "\n".join(lines)
    result = post_message(TASK_LEADER_CH_ID, msg)
    print(f"✅ 夜のサマリー投稿完了 (message_id: {result['id']})")

if __name__ == "__main__":
    evening()
