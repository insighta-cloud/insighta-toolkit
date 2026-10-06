provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge({
      Application        = "insighta-toolkit"
      Component          = "agentcore-financial-rag"
      Environment        = var.environment
      Owner              = var.owner
      CostCenter         = var.cost_center
      DataClassification = var.data_classification
      ManagedBy          = "OpenTofu"
      Migration          = "agentcore-s3-vectors"
    }, var.additional_tags)
  }
}

data "aws_caller_identity" "current" {}

locals {
  resource_prefix    = "${var.name_prefix}-${data.aws_caller_identity.current.account_id}-${var.aws_region}"
  data_bucket_name   = "${local.resource_prefix}-data"
  vector_bucket_name = "${local.resource_prefix}-vectors"
  vector_index_name  = "financial-events"
}

resource "aws_s3_bucket" "records" {
  bucket = local.data_bucket_name
}

resource "aws_s3_bucket_public_access_block" "records" {
  bucket = aws_s3_bucket.records.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "records" {
  bucket = aws_s3_bucket.records.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3vectors_vector_bucket" "financial_events" {
  vector_bucket_name = local.vector_bucket_name
  force_destroy      = false
}

resource "aws_s3vectors_index" "financial_events" {
  index_name         = local.vector_index_name
  vector_bucket_name = aws_s3vectors_vector_bucket.financial_events.vector_bucket_name
  data_type          = "float32"
  dimension          = var.embedding_dimension
  distance_metric    = "cosine"

  # The complete source record is stored in S3. Omitting metadata_configuration
  # makes all index metadata filterable for language, ticker, urgency, and time
  # queries.
}
