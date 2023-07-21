variable "aws_account_alias" {
  description = "AWS account alias"
  type        = string
}

variable "domain" {
  description = "The base domain to be used by the API Gateway"
  type        = string
}

variable "environment" {
  default = "dev"
  type    = string
}

variable "region" {
  default = "us-west-1"
  type    = string
}

variable "stack_name" {
  description = "Name of the Lambda Stack"
  type        = string
  default     = "sample-webhook-handler"
}

variable "subdomain" {
  type    = string
  default = "sample-webhook-handler"
}
