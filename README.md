# OpenClaw Discord Task Manager スキル

Discord フォーラムチャンネルをタスクボードとして使う OpenClaw スキルセット。

## 構成

```
discord-task-manager/   ← ディスパッチャー（TERU_MASTERが読む）
  SKILL.md
  scripts/
    add_task.py         ← タスク追加（スレッド作成 + ヒアリング自動投稿）
    close_task.py       ← タスク完了（完了タグ付け）
    list_tasks.py       ← 未完了タスク一覧
    morning_summary.py  ← 朝サマリー
    evening_summary.py  ← 夜サマリー
    config.py           ← ID・タグID設定

task-executor/          ← 実行担当（スレッドを読んだAIが担う）
  SKILL.md

TASK_SYSTEM_DESIGN.md   ← 設計思想・決断の記録
```

## 設計思想

詳細は [TASK_SYSTEM_DESIGN.md](./TASK_SYSTEM_DESIGN.md) を参照。

- **スレッド = 指示書**（背景・ゴール・制約・完了条件がすべて入る）
- **ディスパッチャー ↔ 実行担当** の役割分離
- **タスクリーダーChは通知専用**（作業はすべてフォーラムスレッド内で完結）
- **subagentに依存しない** — スレッドを読んだAIが誰でも実行担当になれる

## セットアップ

1. `discord-task-manager/scripts/config.py` の各IDを自分の環境に書き換える
2. スキルを `~/clawd/skills/` に配置する
3. OpenClaw の `available_skills` に登録する

## 必要な環境変数

```bash
DISCORD_TOKEN=your_bot_token
```

または `config.py` 内に直接記述。

## 作者

[naoterumaker](https://github.com/naoterumaker)
