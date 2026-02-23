#!/usr/bin/env python3
"""
タスク完了: スレッドをアーカイブ + 完了タグ付け
使い方: python close_task.py <スレッドID>
"""
import sys, json, urllib.request, urllib.error
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *

def close_task(thread_id):
    # まず現在のタグを取得
    req = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}",
        headers=headers(),
    )
    with urllib.request.urlopen(req) as r:
        ch = json.loads(r.read())

    current_tags = ch.get("applied_tags", [])
    # 完了タグを追加（重複しないように）
    if TAGS["完了"] not in current_tags:
        current_tags.append(TAGS["完了"])

    # 優先度タグは残す（ナレッジも残す）
    body = {
        "applied_tags": current_tags,
    }
    req2 = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="PATCH",
    )
    try:
        with urllib.request.urlopen(req2) as r:
            resp = json.loads(r.read())
            print(f"✅ タスク完了: {resp['name']}")
            print(f"   スレッドID: {thread_id}")
    except urllib.error.HTTPError as e:
        print(f"❌ エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: close_task.py <スレッドID>", file=sys.stderr)
        sys.exit(1)
    close_task(sys.argv[1])
