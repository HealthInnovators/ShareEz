variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
}

variable "state_bucket" {
  type        = string
  description = "Bucket name for backend state"
}

variable "log_bucket_name" {
  type        = string
  description = "A bucket to send the Cloudfront logs"
}

variable "us_east_certificate_validation_arn" {
  type        = string
  description = "Arn of the certificate used by Cloudfront. Please note this has to live in us-east-1."
}

variable "domain_name" {
  type        = string
  description = "Domain name for the ShareEz instance"
}

variable "hosted_zone_id" {
  type        = string
  description = "Hosted Zone ID with the domain Name Servers, pass quotes to create a new one from scratch"
}

variable "ip_whitelist" {
  type        = list(string)
  description = "A list of IPs to whitelist for access to the service"
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the ShareEz service"
}

variable "ui_version" {
  type        = string
  description = "Version number for the built ui static files (e.g. v5.0)"
}
