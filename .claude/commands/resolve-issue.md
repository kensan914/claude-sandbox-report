Issue #$ARGUMENTS を PM として実装から完了処理まで一括で対応してください。

以下の手順で進めてください：

## 1. Issue 確認・分析

- GitHub Issue の内容・受け入れ条件・関連仕様書を確認する
- 変更スコープを判定する: **FE のみ** / **BE のみ** / **FE + BE 両方**
- 作業を細かいサブタスクに分解し、TaskCreate でタスクリストを作成する
- ブロッカーや依存関係があれば事前に報告する

## 2. フィーチャーブランチの作成

```bash
git checkout main && git pull
git checkout -b feature/issue-$ARGUMENTS-<短い説明>
```

## 3. 実装

### FE のみ / BE のみの場合

通常の逐次実装を行う。

- TaskUpdate でタスクを in_progress にしてから着手する
- 実装前に関連ファイルを読み、既存パターンに倣う
- 外部サービス（Supabase など）への変更はその場で適用・確認する
- 各サブタスク完了後に TaskUpdate で completed にする

### FE + BE 両方の場合（並列実装）

Git Worktree でワークスペースを分離し、`task` ツール（`general-purpose`）で **2 つのサブエージェントを同時起動**して並列実装する。

#### 3-1. API コントラクトの確定

並列実装を開始する前に、PM が以下を確定して両エージェントの実装の前提とする。

- エンドポイント URL・HTTP メソッド
- リクエスト / レスポンスの Pydantic スキーマ（フィールド名・型・必須/任意）
- エラーレスポンスの形式・ステータスコード
- `docs/API_SCHEME.md` を参照し、必要に応じて更新する

#### 3-2. Git Worktree のセットアップ

> **重要**: Git は同一ブランチを複数のワークツリーで同時にチェックアウトできない。
> そのため、**FE 用・BE 用にサブブランチを作成**し、それぞれのワークツリーに割り当てる。

```bash
# フィーチャーブランチからサブブランチを作成
git branch feature/issue-$ARGUMENTS-frontend
git branch feature/issue-$ARGUMENTS-backend

# 各サブブランチでワークツリーを作成
git worktree add ../worktree-fe feature/issue-$ARGUMENTS-frontend
git worktree add ../worktree-be feature/issue-$ARGUMENTS-backend
```

#### 3-3. 並列エージェントの起動

`task` ツール（`general-purpose`）で 2 つのサブエージェントを**同時に**起動する。
各エージェントのプロンプトに**ワークツリーのパス**と**担当スコープ**を明示すること。

- **バックエンドエージェント**（`../worktree-be/` で作業）
  - `backend/` 配下の実装・テスト・Alembic マイグレーション
  - 実装完了後、サブブランチにコミットする
  - TaskUpdate で in_progress → completed を管理する

- **フロントエンドエージェント**（`../worktree-fe/` で作業）
  - `frontend/` 配下の実装・テスト
  - API コントラクトに基づき実装する（BE 未完了でも型定義を元に先行実装可能）
  - 実装完了後、サブブランチにコミットする
  - TaskUpdate で in_progress → completed を管理する

#### 3-4. 統合

両エージェント完了後、PM がフィーチャーブランチにサブブランチをマージする。

```bash
# フィーチャーブランチに戻る
git checkout feature/issue-$ARGUMENTS-<短い説明>

# 各サブブランチをマージ（ファイル競合なし前提）
git merge feature/issue-$ARGUMENTS-backend
git merge feature/issue-$ARGUMENTS-frontend
```

#### 3-5. OpenAPI 型同期

バックエンドの変更をマージ後、フロントエンドの型定義を再生成して整合性を検証する。

```bash
# バックエンドを起動した状態で frontend/ にて実行
cd frontend && bun run openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts
```

型の差分がある場合はフロントエンドのコードを修正してコミットする。

#### 3-6. 結合確認

- バックエンド: `cd backend && uv run pytest`
- フロントエンド: `cd frontend && bun run vitest run`
- 型チェック: `cd frontend && bun run tsc --noEmit`

#### 3-7. ワークツリーのクリーンアップ

```bash
git worktree remove ../worktree-fe
git worktree remove ../worktree-be
git branch -d feature/issue-$ARGUMENTS-frontend
git branch -d feature/issue-$ARGUMENTS-backend
```

### 並列実装時の注意点

| 項目 | ルール |
| --- | --- |
| ファイル担当の分離 | FE エージェントは `frontend/` のみ、BE エージェントは `backend/` のみ編集する |
| 共有ファイルの編集禁止 | `CLAUDE.md`・`docs/`・`docker-compose.yml` 等は**どちらのエージェントも編集しない**。必要なら PM が統合後に編集する |
| DB マイグレーション | Alembic マイグレーションは BE エージェントのみが作成する。FE は新カラムに依存するコードを書いてよいが、実行時には BE マージ後のスキーマが必要 |
| 型の自動生成 | `frontend/src/types/api.d.ts` は openapi-typescript で生成するため手動編集しない。統合フェーズ（3-5）で再生成する |
| 外部サービス変更 | Supabase 等への変更は BE エージェントのみが行い、二重適用を防ぐ |
| コミットメッセージ | サブブランチのコミットにも Issue 番号 `#$ARGUMENTS` を含める |

## 4. コミット・プッシュ・PR 作成

```bash
# フィーチャーブランチ上で最終コミット（必要な場合）
git add .
git commit -m "feat: <変更の要約> (#$ARGUMENTS)"

# フィーチャーブランチをプッシュ
git push -u origin feature/issue-$ARGUMENTS-<短い説明>

# main 向きの PR を作成
gh pr create --base main --title "<PRタイトル>" --body "closes #$ARGUMENTS"
```

## 5. 受け入れ条件の検証

- Issue に記載された受け入れ条件を 1 つずつ明示的に検証する
- 検証結果を表形式（条件・結果・詳細）でまとめる

## 6. GitHub の完了処理

- 検証結果サマリーを Issue にコメントとして投稿する（`gh issue comment`）
- Issue を closed/completed でクローズする（`gh issue close --reason completed`）
- GitHub Projects のステータスを Done に更新する
  - Project に Issue が未登録の場合は追加してから更新する
