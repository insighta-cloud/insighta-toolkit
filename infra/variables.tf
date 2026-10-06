variable "aws_region" {
  description = "AWS Region in which to create the migration resources."
  type        = string
  default     = "us-east-1"
}

variable "name_prefix" {
  description = "Lowercase prefix for all migration resources."
  type        = string
  default     = "insighta"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,20}[a-z0-9]$", var.name_prefix))
    error_message = "name_prefix must be 3-22 lowercase letters, digits, or hyphens."
  }
}

variable "environment" {
  description = "Deployment environment used for cost allocation and operations tags."
  type        = string
  default     = "development"

  validation {
    condition     = length(trimspace(var.environment)) > 0
    error_message = "environment must not be empty."
  }
}

variable "owner" {
  description = "Team or contact responsible for this deployment."
  type        = string
  default     = "unassigned"
}

variable "cost_center" {
  description = "Cost allocation code for this deployment."
  type        = string
  default     = "unallocated"
}

variable "data_classification" {
  description = "Highest data classification handled by this deployment."
  type        = string
  default     = "internal"
}

variable "additional_tags" {
  description = "Additional organization-specific tags applied to supported AWS resources."
  type        = map(string)
  default     = {}
}

variable "embedding_dimension" {
  description = "Dimension produced by the embedding model used in phase 3."
  type        = number
  default     = 1024

  validation {
    condition     = var.embedding_dimension >= 1 && var.embedding_dimension <= 4096
    error_message = "S3 Vectors supports dimensions from 1 through 4096."
  }
}

variable "embedding_model_id" {
  description = "Bedrock embedding model invoked by the phase 3 ingestion command."
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "chat_model_id" {
  description = "Bedrock model used by the Strands agent in AgentCore Runtime."
  type        = string
  default     = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

variable "chat_foundation_model_id" {
  description = "Foundation model behind the configured inference profile."
  type        = string
  default     = "anthropic.claude-sonnet-4-5-20250929-v1:0"
}

variable "chat_model_regions" {
  description = "Regions a US cross-region inference profile can use for the chat model."
  type        = set(string)
  default     = ["us-east-1", "us-east-2", "us-west-2"]
}
