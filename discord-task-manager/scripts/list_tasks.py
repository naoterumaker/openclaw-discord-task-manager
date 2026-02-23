#!/usr/bin/env python3
"""
アクティブなタスク一覧を取得する
使い方: python list_tasks.py [--json]
"""
import sys, json, urllib.request, urllib.error
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *

TAG_ID_TO_NAME = {v: k for k, v in TAGS.items()}

def list_tasks(as_json=False):
    # guild全体のアクティブスレッドを取得（フォーラム用）
    req = urllib.request.Request(
        f"{API_BASE}/guilds/{GUILD_ID}/threads/active",
        headers=headers(),
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as r:
            guild_data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"❌ エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    tasks = [
        t for t in guild_data.get("threads", [])
        if t.get("parent_id") == FORUM_CHANNEL_ID
        and TAGS["完了"] not in t.get("applied_tags", [])  # 完了タグは除外
    ]

    # タグでラベル付け
    result = []
    for t in tasks:
        tag_names = [TAG_ID_TO_NAME.get(tid, tid) for tid in t.get("applied_tags", [])]
        priority = next((n for n in tag_names if n in ("🔴高","🟡中","🟢低")), "🟡中")
        is_knowledge = "📚ナレッジ" in tag_names
        result.append({
            "id": t["id"],
            "title": t["name"],
            "priority": priority,
            "tags": tag_names,
            "is_knowledge": is_knowledge,
            "url": f"https://discord.com/channels/{GUILD_ID}/{FORUM_CHANNEL_ID}/{t['id']}",
        })

    # 優先度でソート
    order = {"🔴高": 0, "🟡中": 1, "🟢低": 2}
    result.sort(key=lambda x: order.get(x["priority"], 9))

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    # テキスト表示
    if not result:
        print("📭 アクティブなタスクはありません")
        return result

    print(f"📋 アクティブタスク一覧 ({len(result)}件)\n")
    for t in result:
        tags_str = " ".join(t["tags"])
        print(f"{t['priority']} **{t['title']}**")
        print(f"   タグ: {tags_str}")
        print(f"   <{t['url']}>")
        print()
    return result

def list_done_tasks():
    """完了タグが付いたタスク一覧を取得"""
    req = urllib.request.Request(
        f"{API_BASE}/guilds/{GUILD_ID}/threads/active",
        headers=headers(),
        method="GET",
    )
    with urllib.request.urlopen(req) as r:
        guild_data = json.loads(r.read())

    done = [
        t for t in guild_data.get("threads", [])
        if t.get("parent_id") == FORUM_CHANNEL_ID
        and TAGS["完了"] in t.get("applied_tags", [])
    ]
    return [{
        "id": t["id"],
        "title": t["name"],
        "tags": [TAG_ID_TO_NAME.get(tid, tid) for tid in t.get("applied_tags", [])],
        "url": f"https://discord.com/channels/{GUILD_ID}/{FORUM_CHANNEL_ID}/{t['id']}",
    } for t in done]

if __name__ == "__main__":
    as_json = "--json" in sys.argv
    list_tasks(as_json)
