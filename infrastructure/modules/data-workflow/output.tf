output "athena_query_result_output_bucket_arn" {
  value       = aws_s3_bucket.ShareEz_athena_query_results_bucket.arn
  description = "Output S3 bucket ARN for Athena query results"
}

output "athena_workgroup_arn" {
  value       = aws_athena_workgroup.ShareEz_athena_workgroup.arn
  description = "The arn of the Query workgroup for Athena"
}

output "athena_workgroup_name" {
  value       = aws_athena_workgroup.ShareEz_athena_workgroup.name
  description = "The name of the Query workgroup for Athena"
}

output "catalogue_db_name" {
  value       = aws_glue_catalog_database.catalogue_db.name
  description = "The name of the Glue Catalogue database"
}

output "schema_table_arn" {
  value       = aws_dynamodb_table.schema_table.arn
  description = "The ARN of the DynamoDB schema table"
}

output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}
