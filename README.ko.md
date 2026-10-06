# Insighta Toolkit

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

포함된 다국어 금융 이벤트 JSONL 샘플은 지원되는 두 애플리케이션 경로에서 평가할 수 있습니다.

## 경로 선택

| AWS AgentCore | 로컬 Strands + Bedrock |
| --- | --- |
| OpenTofu, S3 Vectors, AgentCore Runtime으로 Strands 검색 에이전트를 배포합니다. | JSONL 레코드와 벡터 인덱스는 로컬 SQLite에 두고 Bedrock으로 임베딩과 채팅을 실행합니다. |
| [AWS 빠른 시작](docs/getting-started.md) | [로컬 빠른 시작](docs/local-strands.md) |

두 경로는 같은 공개 JSONL 스키마를 사용하며, 근거 기반 답변을 위해 출처 URL을 유지합니다.

## 샘플 데이터셋

포함된 샘플은 60개의 정렬된 이벤트(영어·한국어·일본어 레코드 180개)로 구성됩니다.
공개 JSONL 스키마, 출처 근거, 티커 매핑, 감성 및 긴급도 필드를 확인할 수 있습니다.

전체 **US Financial Events: SEC & Government Sources, Multilingual AI-Ready
Dataset**은 [Datarade](https://datarade.ai/data-products/us-financial-events-sec-government-sources-multilingual-a-insighta-cloud-inc)에서 이용할 수 있습니다.
라이선스 데이터셋 또는 API 접근은 support@insighta.cloud로 문의하세요.

## 라이선스

[LICENSE](LICENSE)를 참고하세요.

## 연락처

insighta cloud Inc. · [insighta.cloud](https://insighta.cloud) · support@insighta.cloud
