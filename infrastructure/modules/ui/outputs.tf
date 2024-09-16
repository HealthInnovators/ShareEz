output "tags" {
  value       = var.tags
  description = "The tags used in the project"
}

output "bucket_public_arn" {
  value       = aws_s3_bucket.ShareEz_ui.arn
  description = "The arn of the public S3 bucket"
}

output "bucket_website_domain" {
  value       = aws_s3_bucket_website_configuration.ShareEz_ui_website.website_domain
  description = "The domain of the website endpoint"
}
