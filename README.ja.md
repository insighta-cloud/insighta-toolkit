# Insighta Toolkit

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

同梱の多言語金融イベントJSONLサンプルは、サポートする二つのアプリケーション経路で評価できます。

## 経路を選ぶ

| AWS AgentCore | ローカルStrands + Bedrock |
| --- | --- |
| OpenTofu、S3 Vectors、AgentCore RuntimeでStrands検索エージェントをデプロイします。 | JSONLレコードとベクトルインデックスはローカルSQLiteに保持し、Bedrockで埋め込みとチャットを実行します。 |
| [AWSクイックスタート](docs/getting-started.md) | [ローカルクイックスタート](docs/local-strands.md) |

どちらも同じ公開JSONLスキーマを使用し、根拠に基づく回答のため出典URLを維持します。

## サンプルデータセット

同梱サンプルは60件の整列済みイベント（英語・韓国語・日本語の計180レコード）です。
公開JSONLスキーマ、出典の裏付け、ティッカーマッピング、センチメント、緊急度のフィールドを確認できます。

完全版の **US Financial Events: SEC & Government Sources, Multilingual
AI-Ready Dataset** は [Datarade](https://datarade.ai/data-products/us-financial-events-sec-government-sources-multilingual-a-insighta-cloud-inc) から利用できます。
ライセンス済みデータセットまたはAPIアクセスについては support@insighta.cloud までお問い合わせください。

## ライセンス

[LICENSE](LICENSE)を参照してください。

## 連絡先

insighta cloud Inc. · [insighta.cloud](https://insighta.cloud) · support@insighta.cloud
