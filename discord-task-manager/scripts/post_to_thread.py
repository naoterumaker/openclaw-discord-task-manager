#!/usr/bin/env python3
"""
フォーラムスレッド内に作業進捗・結果を投稿する
使い方: python post_to_thread.py <スレッドID> <メッセージ>
"""
import sys, json, urllib.request, urllib.error
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *

def post_to_thread(thread_id, content):
    body = {"content": content}
    req = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}/messages",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
            print(f"✅ スレッド内投稿完了 (message_id: {resp['id']})")
            return resp["id"]
    except urllib.error.HTTPError as e:
        print(f"❌ エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

def notify_task_leader(content):
    """タスクリーダーチャンネルに通知（開始・エラー・承認依頼のみ）"""
    body = {"content": content}
    req = urllib.request.Request(
        f"{API_BASE}/channels/{TASK_LEADER_CH_ID}/messages",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: post_to_thread.py <スレッドID> <メッセージ>", file=sys.stderr)
        sys.exit(1)
    post_to_thread(sys.argv[1], sys.argv[2])
