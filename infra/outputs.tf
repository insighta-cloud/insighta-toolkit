output "records_bucket_name" {
  description = "Normal S3 bucket that stores canonical source records."
  value       = aws_s3_bucket.records.bucket
}

output "vector_bucket_arn" {
  description = "S3 Vector Bucket ARN."
  value       = aws_s3vectors_vector_bucket.financial_events.vector_bucket_arn
}

output "vector_bucket_name" {
  description = "S3 Vector Bucket name used by the ingestion command."
  value       = aws_s3vectors_vector_bucket.financial_events.vector_bucket_name
}

output "vector_index_arn" {
  description = "S3 Vectors index ARN used by ingestion and runtime."
  value       = aws_s3vectors_index.financial_events.index_arn
}

output "ingestion_role_arn" {
  description = "Role for the phase 3 ingestion command."
  value       = aws_iam_role.ingestion.arn
}

output "runtime_role_arn" {
  description = "Role reserved for the phase 4 AgentCore runtime."
  value       = aws_iam_role.runtime.arn
}

output "agent_runtime_arn" {
  description = "AgentCore Runtime ARN for the Strands financial agent."
  value       = aws_bedrockagentcore_agent_runtime.insighta.agent_runtime_arn
}
