variable "tags" {
  type        = map(string)
  description = "A common map of tags for all VPC resources that are created (for e.g. billing purposes)"
  default = {
    Resource = "data-f1-ShareEz"
  }
}

variable "aws_account" {
  type        = string
  description = "AWS Account number to host the ShareEz service"
}

variable "resource-name-prefix" {
  type        = string
  description = "The prefix to add to resources for easier identification"
}

variable "aws_region" {
  type        = string
  description = "The region of the AWS Account for the ShareEz service"
}
