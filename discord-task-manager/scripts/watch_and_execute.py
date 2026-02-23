#!/usr/bin/env python3
"""
未着手タスクを自動検知してtask-executorを起動するcronウォッチャー

使い方:
  python watch_and_execute.py           # 通常実行
  python watch_and_execute.py --dry-run # 実行せず確認のみ

cron: 1時間ごと（openclaw cron で登録）
state管理: ~/clawd/runs/cron-watch-state.json
"""
import sys, json, os, subprocess, datetime, urllib.request, urllib.error
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from config import *
from list_tasks import list_tasks

STATE_FILE = os.path.expanduser("~/clawd/runs/cron-watch-state.json")

# 自動実行の許可タグ（このタグがあるタスクだけ実行）
ALLOW_TAG = "⏩実行可"

# 除外タグ（これらがついてるタスクは自動実行しない）
SKIP_TAGS = {"⏸ブロック中", "完了"}

# スキップするスレッドID（タスクリーダーChなど管理用チャンネルを除外）
SKIP_THREAD_IDS = {TASK_LEADER_CH_ID}

# task-executorへの指示テンプレート
TASK_EXECUTOR_MSG = """Read ~/clawd/skills/task-executor/SKILL.md and follow it exactly.

以下のタスクスレッドを実行してください：
- スレッドID: {task_id}
- タイトル: {task_title}
- URL: {task_url}

STEP 1: message tool (action=read, target={task_id}) でスレッドを読む
STEP 2: SKILL.md のフローに従って実行（情報不足なら @971703824198824008 にヒアリング）
STEP 3: 完了したらタスクリーダーCh (1475156472072503377) に完了報告

※ このジョブはcronウォッチャーが自動起動しました（てるさん不在時の自動実行）"""


def load_state():
    """処理済みタスクIDの読み込み"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"launched_tasks": {}}


def save_state(state):
    """処理済みタスクIDの保存"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def post_message(channel_id, content):
    """Discordにメッセージを投稿"""
    body = {"content": content}
    req = urllib.request.Request(
        f"{API_BASE}/channels/{channel_id}/messages",
        data=json.dumps(body).encode(),
        headers=headers(),
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def launch_task_executor(task, dry_run=False):
    """タスクに対してtask-executorをisolated cronで起動"""
    task_id = task["id"]
    task_title = task["title"]
    task_url = task["url"]

    message = TASK_EXECUTOR_MSG.format(
        task_id=task_id,
        task_title=task_title,
        task_url=task_url,
    )

    if dry_run:
        print(f"  [DRY-RUN] 起動予定: {task_title}")
        return "dry-run-job-id"

    # openclaw cron add で isolated agent を作成 (+10s で即時起動)
    result = subprocess.run([
        "openclaw", "cron", "add",
        "--name", f"auto-task-{task_id[:8]}",
        "--at", "1m",
        "--session", "isolated",
        "--message", message,
        "--announce",
        "--channel", "discord",
        "--to", f"channel:{TASK_LEADER_CH_ID}",
        "--delete-after-run",
        "--json",
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ cron add 失敗: {result.stderr}", file=sys.stderr)
        return None

    try:
        job_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ cron add レスポンス解析失敗: {result.stdout}", file=sys.stderr)
        return None

    job_id = job_data.get("id") or job_data.get("jobId")
    if not job_id:
        print(f"❌ job_id が取得できませんでした: {job_data}", file=sys.stderr)
        return None

    print(f"🚀 起動: {task_title} (job: {job_id})")
    return job_id


def watch_and_execute(dry_run=False):
    print(f"🔍 未着手タスクを確認中... {'[DRY-RUN]' if dry_run else ''}")

    # アクティブタスク一覧を取得
    tasks = list_tasks(as_json=True)
    if not tasks:
        print("📭 アクティブなタスクはありません")
        return

    state = load_state()
    launched = state.get("launched_tasks", {})

    # 未処理タスクを抽出
    new_tasks = []
    for task in tasks:
        task_id = task["id"]
        task_tags = set(task.get("tags", []))

        # 管理用チャンネルIDはスキップ
        if task_id in SKIP_THREAD_IDS:
            continue

        # ⏩実行可タグがなければスキップ
        if ALLOW_TAG not in task_tags:
            print(f"  ⏭ 待機中（実行可タグなし）: {task['title']}")
            continue

        # スキップタグがあれば除外
        if task_tags & SKIP_TAGS:
            print(f"  ⏭ スキップ: {task['title']} (タグ: {task_tags & SKIP_TAGS})")
            continue

        # 既に起動済みは除外
        if task_id in launched:
            print(f"  ✅ 起動済み: {task['title']}")
            continue

        new_tasks.append(task)

    if not new_tasks:
        print("✅ 新しいタスクはありません（全て起動済みかスキップ済み）")
        state["last_checked"] = datetime.datetime.now().isoformat()
        if not dry_run:
            save_state(state)
        return

    print(f"\n📋 未着手タスク {len(new_tasks)}件を検知！")

    launched_now = []
    for task in new_tasks:
        job_id = launch_task_executor(task, dry_run=dry_run)
        if job_id:
            launched[task["id"]] = {
                "title": task["title"],
                "job_id": job_id,
                "launched_at": datetime.datetime.now().isoformat(),
            }
            launched_now.append(task)

    if not dry_run:
        # stateを更新
        state["launched_tasks"] = launched
        state["last_checked"] = datetime.datetime.now().isoformat()
        save_state(state)

        # タスクリーダーChに通知
        if launched_now:
            lines = ["🤖 **[cronウォッチ] 未着手タスクを自動起動しました**\n"]
            for t in launched_now:
                lines.append(f"🚀 {t['priority']} **{t['title']}**")
                lines.append(f"   <{t['url']}>")
            lines.append("\n_てるさん不在中に自動実行開始。完了時に報告します。_")
            post_message(TASK_LEADER_CH_ID, "\n".join(lines))

    print(f"\n✅ {len(launched_now)}件のタスクを起動しました")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    watch_and_execute(dry_run=dry_run)
