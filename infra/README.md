# OpenTofu infrastructure

This is the supported infrastructure root. It creates normal S3 storage,
an S3 Vectors index, least-privilege ingestion/runtime roles, and an
AgentCore Runtime hosting the Strands agent. It does not create a Bedrock
Knowledge Base, OpenSearch collection, or Bedrock Agent.

The ingestion role can invoke Titan Text Embeddings V2 but cannot invoke a
generative model. Build the runtime package before planning or applying:

```bash
uv run python tools/build_runtime_bundle.py
```

## Verify and plan

```bash
cd infra
tofu init
tofu fmt -check -recursive
tofu validate
tofu plan
```

`tofu apply` is deliberately a separate, explicit action. Use an AWS Region
where S3 Vectors and the planned embedding model are available. State is local
for this example; configure a remote backend before shared or production use.

## Resource tags

Supported AWS resources receive common tags for ownership, cost allocation,
and data handling. Set organization-specific values in an ignored
`terraform.tfvars` file or on the command line:

```hcl
environment         = "production"
owner               = "data-platform"
cost_center         = "FIN-001"
data_classification = "confidential"
additional_tags = {
  Project = "financial-intelligence"
}
```

The default values (`development`, `unassigned`, and `unallocated`) are
deliberately conspicuous so production deployments do not silently inherit
meaningful ownership or billing labels.

The default `embedding_dimension` is 1024, matching the planned Titan Text
Embeddings V2 configuration. Change it only together with the phase 3
embedding model configuration, because an S3 Vectors index dimension is
immutable.
