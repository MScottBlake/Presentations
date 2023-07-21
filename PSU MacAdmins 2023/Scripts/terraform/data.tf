data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

data "aws_vpc" "sample" {
  filter {
    name   = "tag:Name"
    values = [var.aws_account_alias]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.sample.id]

  }
  tags = {
    Name = "${var.aws_account_alias}-private-*"
  }
}

data "cloudflare_zone" "this" {
  name = var.domain
}
