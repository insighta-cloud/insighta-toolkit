data "archive_file" "agent_runtime" {
  type        = "zip"
  source_dir  = "${path.module}/../.runtime-package"
  output_path = "${path.module}/.build/insighta-agent-runtime.zip"
}

resource "aws_s3_object" "agent_runtime_code" {
  bucket = aws_s3_bucket.records.id
  key    = "runtime/insighta-agent-runtime.zip"
  source = data.archive_file.agent_runtime.output_path
  # AgentCore bundles exceed the S3 multipart threshold, so the remote ETag
  # is not an MD5 checksum. Keep the local source checksum in state instead.
  source_hash = filemd5(data.archive_file.agent_runtime.output_path)
}

resource "aws_bedrockagentcore_agent_runtime" "insighta" {
  agent_runtime_name = "${replace(var.name_prefix, "-", "_")}_financial_intelligence"
  description        = "Strands financial RAG agent using S3 Vectors."
  role_arn           = aws_iam_role.runtime.arn

  agent_runtime_artifact {
    code_configuration {
      entry_point = ["main.py"]
      runtime     = "PYTHON_3_13"

      code {
        s3 {
          bucket = aws_s3_bucket.records.id
          prefix = aws_s3_object.agent_runtime_code.key
        }
      }
    }
  }

  environment_variables = {
    AWS_REGION         = var.aws_region
    CHAT_MODEL_ID      = var.chat_model_id
    EMBEDDING_MODEL_ID = var.embedding_model_id
    RECORDS_BUCKET     = aws_s3_bucket.records.id
    VECTOR_BUCKET      = aws_s3vectors_vector_bucket.financial_events.vector_bucket_name
    VECTOR_INDEX       = aws_s3vectors_index.financial_events.index_name
    RUNTIME_BUNDLE_SHA = data.archive_file.agent_runtime.output_base64sha256
  }

  network_configuration {
    network_mode = "PUBLIC"
  }
}
