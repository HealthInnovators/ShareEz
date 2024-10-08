variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
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

variable "catalog_disabled" {
  type        = bool
  description = "Optional value on whether to disable the internal ShareEz data catalog"
  default     = false
}

variable "ShareEz_ecr_url" {
  type        = string
  description = "ECR Url for task definition"
  default     = "public.ecr.aws/no10-ShareEz/api"
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

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the ShareEz service"
}

variable "state_bucket" {
  type        = string
  description = "Bucket name for backend state"
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

variable "support_emails_for_cloudwatch_alerts" {
  type        = list(string)
  description = "List of emails that will receive alerts from CloudWatch"
}

variable "project_information" {
  type = object({
    project_name         = optional(string),
    project_description  = optional(string),
    project_contact      = optional(string),
    project_organisation = optional(string)
  })

  default = {}
}

variable "layers" {
  type        = list(string)
  description = "A list of the layers that the ShareEz instance will contain"
  default     = ["default"]
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
