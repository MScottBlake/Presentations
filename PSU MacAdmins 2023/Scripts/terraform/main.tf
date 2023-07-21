provider "aws" {
  region = var.region

  default_tags {
    tags = {
      environment = var.environment
      owner       = "IT"
      application = "Sample Webhook Handler"
    }
  }
}

provider "cloudflare" {}

provider "docker" {
  registry_auth {
    address  = "${data.aws_caller_identity.this.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com"
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}
