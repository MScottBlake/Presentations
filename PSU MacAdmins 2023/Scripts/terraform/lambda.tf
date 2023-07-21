module "sample_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 4.12.1"

  function_name = "${var.stack_name}-lambda-enroll"

  create_package = false
  publish        = true

  image_uri    = module.sample_docker_image.image_uri
  package_type = "Image"
  timeout      = 60

  attach_network_policy  = true
  vpc_subnet_ids         = data.aws_subnets.private.ids
  vpc_security_group_ids = [module.security_group.security_group_id]

  environment_variables = {
    ENVIRONMENT = var.environment
    LOG_LEVEL   = "INFO"
  }

  allowed_triggers = {
    AllowAPIGatewayPostEnroll = {
      service    = "apigateway"
      source_arn = "${module.api_gateway.apigatewayv2_api_execution_arn}/*/POST/v1/sample"
    }
  }

  depends_on = [module.sample_docker_image]
}

module "sample_docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"

  create_ecr_repo = true
  ecr_repo        = "${var.environment}/${var.stack_name}-lambda-image"
  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 2 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 2
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })

  source_path      = "../lambdas/sample_with_requirements"
  docker_file_path = "Dockerfile"
  platform         = "linux/amd64"
}
