module "api_gateway" {
  source = "terraform-aws-modules/apigateway-v2/aws"

  name          = "${var.stack_name}-api-gateway"
  description   = "Sample Wekhook Handler - HTTP API Gateway"
  protocol_type = "HTTP"

  cors_configuration = {
    allow_headers = ["authorization", "content-type", "x-amz-date", "x-amz-security-token", "x-amz-user-agent", "x-api-key"]
    allow_methods = ["*"]
    allow_origins = ["*"]
  }

  # Custom Domain
  domain_name                 = "${var.subdomain}.${var.domain}"
  domain_name_certificate_arn = module.acm.acm_certificate_arn

  # Access logs
  default_stage_access_log_destination_arn = aws_cloudwatch_log_group.api_gateway.arn
  default_stage_access_log_format          = "$context.identity.sourceIp - - [$context.requestTime] \"$context.httpMethod $context.routeKey $context.protocol\" $context.status $context.responseLength $context.requestId $context.integrationErrorMessage"

  # Routes and integrations
  integrations = {
    "POST /v1/sample" = {
      authorization_type     = "NONE"
      lambda_arn             = module.sample_lambda.lambda_function_invoke_arn
      payload_format_version = "2.0"
      timeout_milliseconds   = 20000
    }
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/api_gateway/${module.api_gateway.apigatewayv2_api_id}"
  retention_in_days = 30
}
