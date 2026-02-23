#!/usr/bin/env python3
"""
タスクスレッドのタグを追加/削除するユーティリティ

使い方:
  python tag_task.py <スレッドID> --add "⏩実行可"
  python tag_task.py <スレッドID> --remove "⏸ブロック中"
  python tag_task.py <スレッドID> --add "⏩実行可" --remove "⏸ブロック中"
"""
import sys, json, urllib.request, urllib.error, argparse
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *

TAG_ID_TO_NAME = {v: k for k, v in TAGS.items()}


def get_thread(thread_id):
    req = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}",
        headers=headers(), method="GET",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def update_tags(thread_id, add_tags=None, remove_tags=None):
    thread = get_thread(thread_id)
    current_tag_ids = set(thread.get("applied_tags", []))

    # タグを追加
    for tag_name in (add_tags or []):
        tag_id = TAGS.get(tag_name)
        if not tag_id:
            print(f"❌ タグ名が見つかりません: {tag_name}", file=sys.stderr)
            print(f"   利用可能: {list(TAGS.keys())}", file=sys.stderr)
            continue
        current_tag_ids.add(tag_id)
        print(f"  ➕ 追加: {tag_name}")

    # タグを削除
    for tag_name in (remove_tags or []):
        tag_id = TAGS.get(tag_name)
        if not tag_id:
            print(f"❌ タグ名が見つかりません: {tag_name}", file=sys.stderr)
            continue
        current_tag_ids.discard(tag_id)
        print(f"  ➖ 削除: {tag_name}")

    # 更新
    body = {"applied_tags": list(current_tag_ids)}
    req = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}",
        data=json.dumps(body).encode(),
        headers=headers(), method="PATCH",
    )
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
        final_tags = [TAG_ID_TO_NAME.get(tid, tid) for tid in result.get("applied_tags", [])]
        print(f"✅ タグ更新完了: {final_tags}")
        return result
    except urllib.error.HTTPError as e:
        print(f"❌ エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="タスクスレッドのタグを追加/削除する")
    parser.add_argument("thread_id", help="スレッドID")
    parser.add_argument("--add", "-a", action="append", default=[], help="追加するタグ名（複数可）")
    parser.add_argument("--remove", "-r", action="append", default=[], help="削除するタグ名（複数可）")
    a = parser.parse_args()

    if not a.add and not a.remove:
        parser.print_help()
        sys.exit(1)

    update_tags(a.thread_id, a.add, a.remove)
