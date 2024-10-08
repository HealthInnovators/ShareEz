variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default = {
    Resource = "data-f1-ShareEz"
  }
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "app-replica-count-desired" {
  type        = number
  description = "The desired number of replicas of the app"
  default     = 1
}

variable "app-replica-count-max" {
  type        = number
  description = "The maximum desired number of replicas of the app"
  default     = 2
}

variable "container_port" {
  type        = number
  description = "The port for the running ECS containers"
  default     = 8000
}

variable "host_port" {
  type        = number
  description = "The host port for the running ECS containers"
  default     = 8000
}

variable "protocol" {
  type        = string
  description = "The protocol for the running ECS container"
  default     = "tcp"
}

variable "catalog_disabled" {
  type        = bool
  description = "Optional value on whether to disable the internal ShareEz data catalog"
  default     = false
}

variable "ShareEz_ecr_url" {
  type        = string
  description = "ECR Url for task definition"
}

variable "data_s3_bucket_arn" {
  type        = string
  description = "S3 Bucket arn to store application data"
}

variable "data_s3_bucket_name" {
  type        = string
  description = "S3 Bucket name to store application data"
}

variable "vpc_id" {
  type        = string
  description = "Application VPC"
}

variable "private_subnet_ids_list" {
  type        = list(string)
  description = "Application Private subnet list"
}

variable "public_subnet_ids_list" {
  type        = list(string)
  description = "Application Public subnet list"
}

variable "application_version" {
  type        = string
  description = "The version number for the application image (e.g.: v1.0.4, v1.0.x-latest, etc.)"
}

variable "domain_name" {
  type        = string
  description = "Domain name for the ShareEz instance"
}

variable "allowed_email_domains" {
  type        = string
  description = "List of allowed emails domains that can be associated with users"
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the ShareEz service"
}

variable "hosted_zone_id" {
  type        = string
  description = "Hosted Zone ID with the domain Name Servers, pass quotes to create a new one from scratch"
}

variable "certificate_validation_arn" {
  type        = string
  description = "Arn of the certificate used by the domain"
}

variable "ip_whitelist" {
  type        = list(string)
  description = "A list of IPs to whitelist for access to the service"
}

variable "enable_cloudtrail" {
  type        = bool
  description = "Whether to enable the logging of db events to CloudTrail"
  default     = true
}

variable "athena_query_output_bucket_arn" {
  type        = string
  description = "The S3 bucket ARN where Athena stores its query results. This bucket is created dynamically with a unique name in the data-workflow module. Reference it by remote state, module output or ARN string directly"
}

variable "permissions_table_arn" {
  type        = string
  description = "Users permissions table arn in dynamoDB"
}

variable "schema_table_arn" {
  type        = string
  description = "The ARN of the schema table in dynamoDB"
}

variable "catalogue_db_name" {
  type        = string
  description = "The name of the catalogue db in dynamoDB"
}

variable "cognito_user_pool_id" {
  type        = string
  description = "User pool id for cognito"
}

variable "cognito_user_login_app_credentials_secrets_name" {
  type        = string
  description = "Secret name for Cognito user login app credentials"
}

variable "support_emails_for_cloudwatch_alerts" {
  type        = list(string)
  description = "List of emails that will receive alerts from CloudWatch"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the ShareEz service"
}

variable "log_bucket_name" {
  type        = string
  description = "A bucket to send the Load Balancer logs"
}

variable "project_information" {
  type = object({
    project_name         = optional(string),
    project_description  = optional(string),
    project_contact      = optional(string),
    project_organisation = optional(string)
  })

  default = {
    project_name         = "",
    project_description  = "",
    project_contact      = "",
    project_organisation = ""
  }
}

variable "ecs_cluster_id" {
  type        = string
  default     = null
  description = "ECS cluster id to attach the ShareEz api to"
}

variable "ecs_cluster_arn" {
  type        = string
  default     = null
  description = "ECS cliuster arn to attach the ShareEz api to"
}

variable "ecs_cluster_name" {
  type        = string
  default     = null
  description = "ECS cluster name to attach the ShareEz api to"
}

variable "layers" {
  type        = list(string)
  description = "A list of the layers that the ShareEz instance will contain"
  default     = ["default"]
}

variable "custom_user_name_regex" {
  type        = string
  description = "A regex expression for conditional user validation."
  default     = null
  nullable    = true
}

variable "task_memory" {
  type        = number
  description = "ShareEz ecs task memory"
  default     = 512
}

variable "task_cpu" {
  type        = number
  description = "ShareEz ecs task cpu"
  default     = 256
}
