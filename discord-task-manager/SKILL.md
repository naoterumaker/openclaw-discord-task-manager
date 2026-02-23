---
name: discord-task-manager
description: Discordフォーラムチャンネルをタスクボードとして使うタスク管理スキル。「タスク追加」「タスク完了」「タスクリスト」「朝サマリー」「夜サマリー」などで発火。TERU_MASTERのディスパッチャー役スキル。
---

# Discord Task Manager（ディスパッチャー）

TERU_MASTERはタスクの「振り役」。実行は指示書を読んだAIが担う。

---

## 🗺 全体フロー

```
てるさん → 「〇〇タスクやって」
  ↓
TERU_MASTER
  1. フォーラムスレッドを即作成（タイトルと骨格だけ）
  2. スレッド内で @てるさん にヒアリング開始
     「背景・完了条件・制約・締め切りを教えてください」
  ↓
てるさん → スレッド内で返答
  ↓
TERU_MASTER or 実行担当
  3. スレッドに情報が揃ったら指示書を更新
  4. task-executor スキルに従って実行
  5. 作業詳細・進捗はすべてスレッド内に投稿
  ↓
完了 → タスクリーダーChに通知のみ
  ↓
てるさんが承認 → クローズ
```

**ポイント：会話・ヒアリング・作業・完了まで全部フォーラムスレッド内で完結。タスクリーダーChは通知専用。**

---

## 📂 チャンネル構成

| 場所 | 何を書く |
|------|---------|
| **タスクリーダーCh** | 🟢開始通知 / 🔴エラー / ✅完了承認依頼 のみ |
| **フォーラムスレッド内** | 指示書・作業詳細・進捗・調査結果 |

---

## タグ

| タグ | 用途 |
|------|------|
| 🔴高 | 優先度: 高 |
| 🟡中 | 優先度: 中（デフォルト） |
| 🟢低 | 優先度: 低 |
| 📚ナレッジ | 調査系（完了後もスレッドを残す） |
| 完了 | 完了済み |
| ⏸ブロック中 | 依存タスク待ち |

---

## ワークフロー 1: タスク追加 → ヒアリング開始

### パターンA：情報不足（デフォルト）
```bash
python ~/clawd/skills/discord-task-manager/scripts/add_task.py \
  --title "タイトル" \
  --priority 高|中|低 \
  [--knowledge]
```
→ スレッド作成 + スレッド内で自動ヒアリングメッセージを投稿
→ てるさんがスレッド内で答えたら作業開始

### パターンB：情報が揃っている場合
```bash
python ~/clawd/skills/discord-task-manager/scripts/add_task.py \
  --title "タイトル" \
  --priority 高|中|低 \
  --body "背景・ゴール・制約・締め切りを含む詳細説明" \
  [--knowledge]
```
→ スレッド作成 + 指示書に詳細が入る → ヒアリングなしで即実行可能

---

## ワークフロー 2: タスク一覧確認

```bash
python ~/clawd/skills/discord-task-manager/scripts/list_tasks.py
python ~/clawd/skills/discord-task-manager/scripts/list_tasks.py --json
```

---

## ワークフロー 3: タスククローズ（てるさん承認後）

```bash
python ~/clawd/skills/discord-task-manager/scripts/close_task.py <スレッドID>
```

---

## ワークフロー 4: 朝サマリー（cron 8:10）

```bash
python ~/clawd/skills/discord-task-manager/scripts/morning_summary.py
```

---

## ワークフロー 5: 夜サマリー（cron 22:00）

```bash
python ~/clawd/skills/discord-task-manager/scripts/evening_summary.py
```

---

## ユーザー指示の解釈

| てるさんの言葉 | アクション |
|--------------|-----------|
| 「タスク追加：〇〇」「〇〇をタスクに入れて」 | add_task.py 実行 |
| 「タスク一覧」「何が残ってる？」 | list_tasks.py 実行 |
| 「〇〇完了」「〇〇終わった」 | list_tasks.py でID特定 → close_task.py |
| 「調査タスク：〇〇」 | add_task.py に --knowledge を付けて実行 |
| 「依存あり」「これ終わったら」 | ⏸ブロック中タグ + スレッド本文に依存先URL |

---

## 📌 重要ID

- **ギルドID**: `1474320833269993475`
- **フォーラムCh**: `1475147089871769643`（🤖-teru_masterタスク）
- **タスクリーダーCh**: `1475156472072503377`
- **てるさんのDiscord ID**: `971703824198824008`

---

## 関連スキル

- **実行担当用**: `~/clawd/skills/task-executor/SKILL.md`
