#!/usr/bin/env python3
"""
タスクをフォーラムに追加する
使い方: python add_task.py --title "タイトル" [--priority 高|中|低] [--body "説明"] [--knowledge] [--skip-hearing]
"""
import sys, json, urllib.request, urllib.error
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *

# スレッド本文（指示書の骨格）
TASK_TEMPLATE = """## 📋 依頼内容
{description}

---
## 🛠 実行スキル
`/Users/naoterun/clawd/skills/task-executor/SKILL.md`

## ✅ 完了したら
<#1475156472072503377> に完了報告を投稿し、クローズ承認を依頼する。
"""

# スレッド作成直後に投稿するヒアリングメッセージ
HEARING_MESSAGE = """<@971703824198824008>

「{title}」のタスクスレッドを作成しました。

作業を始めるために以下を教えてください 🙏

1. **背景・目的** — なぜこのタスクが必要ですか？
2. **完了条件** — どうなったら「完了」ですか？
3. **制約・注意点** — 守るべきことはありますか？
4. **締め切り** — いつまでに必要ですか？（なければ「なし」でOK）
5. **自律実行OK？** — てるさん不在中（寝てる間・外出中）でも勝手に進めていいですか？（はい/いいえ）
   → **はい** → ⏩実行可タグを付けます（cronが自動起動）
   → **いいえ** → てるさんが確認できるタイミングで実行します

教えていただいた内容を指示書に反映して作業開始します。"""


def post_message(thread_id, content):
    """スレッドにメッセージを投稿する"""
    req = urllib.request.Request(
        f"{API_BASE}/channels/{thread_id}/messages",
        data=json.dumps({"content": content}).encode(),
        headers=headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"⚠️ メッセージ投稿エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        return None


def add_task(title, priority="中", description="", is_knowledge=False, skip_hearing=False, autonomous=False):
    tag_ids = [TAGS[PRIORITY_TAG.get(priority, "🟡中")]]
    if is_knowledge:
        tag_ids.append(TAGS["📚ナレッジ"])
    if autonomous:
        tag_ids.append(TAGS["⏩実行可"])

    # 指示書本文（description がなければ「ヒアリング待ち」と明記）
    body_text = description if description else "（ヒアリング中 — 下のメッセージを確認してください）"
    content = TASK_TEMPLATE.format(description=body_text)

    body = {
        "name": title,
        "message": {"content": content},
        "applied_tags": tag_ids,
    }
    req = urllib.request.Request(
        f"{API_BASE}/channels/{FORUM_CHANNEL_ID}/threads",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            resp = json.loads(r.read())
            thread_id = resp["id"]
            url = f"https://discord.com/channels/{GUILD_ID}/{FORUM_CHANNEL_ID}/{thread_id}"
            print(f"✅ タスク追加完了: {title}")
            print(f"   スレッドID: {thread_id}")
            print(f"   優先度: {priority} | ナレッジ: {is_knowledge}")
            print(f"   URL: {url}")

            # ヒアリングメッセージを投稿（skip_hearing=False かつ description が空の場合）
            if not skip_hearing and not description:
                msg = HEARING_MESSAGE.format(title=title)
                result = post_message(thread_id, msg)
                if result:
                    print(f"   💬 ヒアリングメッセージ投稿済み")

            return thread_id
    except urllib.error.HTTPError as e:
        print(f"❌ エラー: {e.status} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="タスクをフォーラムに追加する")
    parser.add_argument("--title", "-t", required=True, help="タスクタイトル")
    parser.add_argument("--priority", "-p", default="中", choices=["高","中","低"], help="優先度（高|中|低）")
    parser.add_argument("--body", "-b", default="", help="タスク説明（指定するとヒアリングをスキップ）")
    parser.add_argument("--knowledge", "-k", action="store_true", help="ナレッジタスクとして登録")
    parser.add_argument("--skip-hearing", action="store_true", help="ヒアリングメッセージを投稿しない")
    parser.add_argument("--autonomous", "-a", action="store_true", help="⏩実行可タグを付ける（cron自律実行を許可）")
    a = parser.parse_args()
    add_task(a.title, a.priority, a.body, a.knowledge, a.skip_hearing, a.autonomous)
