data "aws_iam_policy_document" "account_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }
}

resource "aws_iam_role" "ingestion" {
  name               = "${local.resource_prefix}-ingestion"
  assume_role_policy = data.aws_iam_policy_document.account_assume_role.json
}

data "aws_iam_policy_document" "ingestion" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.records.arn]
  }

  statement {
    actions = ["s3:GetObject", "s3:PutObject"]
    resources = [
      "${aws_s3_bucket.records.arn}/records/*",
      "${aws_s3_bucket.records.arn}/manifests/*",
    ]
  }

  statement {
    actions = [
      "s3vectors:PutVectors",
      "s3vectors:GetVectors",
      "s3vectors:DeleteVectors",
    ]
    resources = [aws_s3vectors_index.financial_events.index_arn]
  }

  statement {
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.embedding_model_id}",
    ]
  }
}

resource "aws_iam_role_policy" "ingestion" {
  name   = "${local.resource_prefix}-ingestion"
  role   = aws_iam_role.ingestion.id
  policy = data.aws_iam_policy_document.ingestion.json
}

data "aws_iam_policy_document" "runtime_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["bedrock-agentcore.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "runtime" {
  name               = "${local.resource_prefix}-runtime"
  assume_role_policy = data.aws_iam_policy_document.runtime_assume_role.json
}

data "aws_iam_policy_document" "runtime" {
  statement {
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.records.arn}/records/*",
      "${aws_s3_bucket.records.arn}/runtime/*",
    ]
  }

  statement {
    actions = [
      "s3vectors:QueryVectors",
      "s3vectors:GetVectors",
    ]
    resources = [aws_s3vectors_index.financial_events.index_arn]
  }

  statement {
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = concat(
      [
        "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.embedding_model_id}",
        "arn:aws:bedrock:${var.aws_region}:${data.aws_caller_identity.current.account_id}:inference-profile/${var.chat_model_id}",
      ],
      [
        for region in var.chat_model_regions :
        "arn:aws:bedrock:${region}::foundation-model/${var.chat_foundation_model_id}"
      ],
    )
  }
}

resource "aws_iam_role_policy" "runtime" {
  name   = "${local.resource_prefix}-runtime"
  role   = aws_iam_role.runtime.id
  policy = data.aws_iam_policy_document.runtime.json
}
