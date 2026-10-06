# Insighta Toolkit

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

Insighta Toolkitは、金融イベント検索アプリケーションを構築するための参照実装です。
多言語イベントJSONLを検索可能な根拠に変換し、元の情報源URLを引用する回答を返せます。

このリポジトリの中心はデータセットではなく**ツールキット**です。アプリケーション構造、
検索契約、デプロイ方法を実行し、自社のデータとモデルに合わせて拡張できます。同梱JSONLは
コードを試すための小さな入力データです。

## 実行できる二つの経路

| 経路 | 実行内容 | 適した用途 |
| --- | --- | --- |
| **ローカルStrands + Bedrock** | JSONLとベクトル検索はローカルSQLiteに、埋め込みとチャットはBedrockに置きます。 | 一台のマシンでワークフローと検索結果を直接確認する場合 |
| **AWS AgentCore** | AgentCore RuntimeでStrands検索エージェントを実行し、OpenTofuでS3・S3 Vectorsを構成します。 | デプロイ可能なAWS参照アーキテクチャが必要な場合 |

どちらもモデル回答を事実として扱わず、検索されたレコードから回答を作ります。結果には元の
イベントURLが残るため、利用者は根拠を開いて確認できます。

## 仕組み

```text
JSONLイベントレコード
        │
        ├── id・言語・タイトル・本文・メタデータを検証
        ├── 言語別の検索ドキュメントを作成
        ├── タイトル + 本文を埋め込み
        └── 質問に関連するレコードを検索
                                      │
                                      ▼
                         情報源URLを含む
                         Strandsエージェント回答
```

共有レコード契約は、論理イベントの`id`、言語別の`title`・`content`、ティッカー、緊急度・
センチメント、出所メタデータを定義します。ローカルとAWS経路は同じ契約を使います。

## ローカルで始める

選択したBedrockモデルを使えるAWS認証情報を設定してから、サンプルをインデックス化します。

```bash
export AWS_PROFILE=<your-profile>
uv sync --extra local
uv run --extra local python -m apps.local.main index sample/202608_60x3.jsonl
uv run --extra local python -m apps.local.main chat "緊急度の高いイベントを要約し、情報源URLを引用してください。"
```

インデックスはGitから除外される`.local/insighta.db`に保存されます。詳細は
[ローカルクイックスタート](docs/local-strands.md)を参照してください。

## AWS参照経路をデプロイする

AWS経路は`apps/agentcore`をパッケージ化し、OpenTofuでランタイムとベクトルストレージを
構成して、同じJSONL契約を取り込みます。手順は
[AWS AgentCoreクイックスタート](docs/getting-started.md)を参照してください。

## 同梱サンプル

[`sample/202608_60x3.jsonl`](sample/202608_60x3.jsonl)はToolkit用の小規模な多言語テスト
入力です。60件の論理イベントと180件のレコードで構成され、各イベントには英語（`en`）、
韓国語（`ko`）、日本語（`ja`）が一件ずつあります。UTF-8 JSONLのパース、多言語検索、
ティッカー・緊急度によるフィルタリング、回答と情報源URLの返却を確認できます。

| フィールド | Toolkitでの用途 |
| --- | --- |
| `id`, `language` | 一つのイベントに属する三言語レコードを対応付けます。 |
| `title`, `content` | 埋め込み・検索層に送るテキストです。 |
| `tickers`, `urgency_level`, `sentiment_score` | 構造化されたフィルタリングと順位付けを支えます。 |
| `source`, `source_name`, `author`, `created_at` | 回答とともに出所情報を表示します。 |

サンプルは評価用入力であり、リアルタイムフィードや投資助言ではありません。重要な利用では
生成された回答を必ずリンク先の一次情報と照合してください。

## リポジトリ構成

```text
apps/local/       ローカルStrandsアプリケーションとSQLiteベクトルストア
apps/agentcore/   AgentCore Runtimeエントリポイント
infra/            AWS参照経路用OpenTofu構成
src-python/       共有JSONL取り込み・検索・ドキュメントhelper
sample/           公開JSONLテスト入力
docs/             ローカルおよびAWSクイックスタート
tests/            共有検索契約のユニットテスト
```

## ライセンス

SEE LICENSE IN [LICENSE](LICENSE).

## AWSリソースのクリーンアップ

AWS参照経路をデプロイした場合は、作成時と同じ`infra/` stateから削除してください。
最初に`tofu plan -destroy`を確認します。records bucketは`tofu destroy`の前に空にする
必要があり、空にするとオブジェクトは恒久的に削除されます。実行前に
[AWSクリーンアップ手順](docs/getting-started.md#clean-up)を確認してください。

## insighta cloudについて

私たちは個人のための投資ワークステーションを構築しています。個人投資家に機関投資家級の
プロセスとツールを提供します。詳しくは
[insighta.cloud/landing](https://insighta.cloud/landing)をご覧ください。

## 連絡先

- **提供者:** insighta cloud Inc.
- **ウェブサイト:** [https://insighta.cloud](https://insighta.cloud)
- **連絡先:** support@insighta.cloud
- **AWS Marketplace:** [販売者プロフィール](https://aws.amazon.com/marketplace/seller-profile?id=seller-ahk55ljrhr4wu)
- **Datarade提供者プロフィール:** [insighta cloud Inc.](https://datarade.ai/data-providers/insighta-cloud-inc/profile)
- **LinkedIn:** [cho-insighta-cloud](https://www.linkedin.com/in/cho-insighta-cloud/)

## 著者

insighta cloud Inc.
