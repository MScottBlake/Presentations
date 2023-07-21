# API Gateway
output "apigatewayv2_api_id" {
  description = "The API identifier"
  value       = module.api_gateway.apigatewayv2_api_id
}

output "apigatewayv2_api_api_endpoint" {
  description = "The URI of the API"
  value       = module.api_gateway.apigatewayv2_api_api_endpoint
}

output "apigatewayv2_api_arn" {
  description = "The ARN of the API"
  value       = module.api_gateway.apigatewayv2_api_arn
}

output "apigatewayv2_api_execution_arn" {
  description = "The ARN prefix to be used in an aws_lambda_permission's source_arn attribute or in an aws_iam_policy to authorize access to the @connections API."
  value       = module.api_gateway.apigatewayv2_api_execution_arn
}

# Default Stage
output "default_apigatewayv2_stage_id" {
  description = "The default stage identifier"
  value       = module.api_gateway.default_apigatewayv2_stage_id
}

output "default_apigatewayv2_stage_arn" {
  description = "The default stage ARN"
  value       = module.api_gateway.default_apigatewayv2_stage_arn
}

output "default_apigatewayv2_stage_execution_arn" {
  description = "The ARN prefix to be used in an aws_lambda_permission's source_arn attribute or in an aws_iam_policy to authorize access to the @connections API."
  value       = module.api_gateway.default_apigatewayv2_stage_execution_arn
}

output "default_apigatewayv2_stage_invoke_url" {
  description = "The URL to invoke the API pointing to the stage"
  value       = module.api_gateway.default_apigatewayv2_stage_invoke_url
}

output "default_apigatewayv2_stage_domain_name" {
  description = "Domain name of the stage (useful for CloudFront distribution)"
  value       = module.api_gateway.default_apigatewayv2_stage_domain_name
}

# Domain Name
output "apigatewayv2_domain_name_id" {
  description = "The domain name identifier"
  value       = module.api_gateway.apigatewayv2_domain_name_id
}

output "apigatewayv2_domain_name_arn" {
  description = "The ARN of the domain name"
  value       = module.api_gateway.apigatewayv2_domain_name_arn
}

output "apigatewayv2_domain_name_api_mapping_selection_expression" {
  description = "The API mapping selection expression for the domain name"
  value       = module.api_gateway.apigatewayv2_domain_name_api_mapping_selection_expression
}

output "apigatewayv2_domain_name_configuration" {
  description = "The domain name configuration"
  value       = module.api_gateway.apigatewayv2_domain_name_configuration
}

output "apigatewayv2_domain_name_target_domain_name" {
  description = "The target domain name"
  value       = module.api_gateway.apigatewayv2_domain_name_target_domain_name
}

output "apigatewayv2_domain_name_hosted_zone_id" {
  description = "The Amazon Route 53 Hosted Zone ID of the endpoint"
  value       = module.api_gateway.apigatewayv2_domain_name_hosted_zone_id
}

# API Mapping
output "apigatewayv2_api_mapping_id" {
  description = "The API mapping identifier."
  value       = module.api_gateway.apigatewayv2_api_mapping_id
}

# ACM
output "acm_certificate_arn" {
  description = "The ARN of the certificate"
  value       = module.acm.acm_certificate_arn
}

output "acm_certificate_domain_validation_options" {
  description = "A list of attributes to feed into other resources to complete certificate validation. Can have more than one element, e.g. if SANs are defined. Only set if DNS-validation was used."
  value       = module.acm.acm_certificate_domain_validation_options
}

output "acm_certificate_status" {
  description = "Status of the certificate."
  value       = module.acm.acm_certificate_status
}

output "distinct_domain_names" {
  description = "List of distinct domains names used for the validation."
  value       = module.acm.distinct_domain_names
}

output "validation_domains" {
  description = "List of distinct domain validation options. This is useful if subject alternative names contain wildcards."
  value       = module.acm.validation_domains
}

# Lambda Function
output "lambda_function_arn" {
  description = "The ARN of the Lambda Function"
  value       = module.sample_lambda.lambda_function_arn
}

output "lambda_function_invoke_arn" {
  description = "The Invoke ARN of the Lambda Function"
  value       = module.sample_lambda.lambda_function_invoke_arn
}

output "lambda_function_name" {
  description = "The name of the Lambda Function"
  value       = module.sample_lambda.lambda_function_name
}

output "lambda_function_qualified_arn" {
  description = "The ARN identifying your Lambda Function Version"
  value       = module.sample_lambda.lambda_function_qualified_arn
}

output "sample_lambda_function_version" {
  description = "Latest published version of Lambda Function"
  value       = module.sample_lambda.lambda_function_version
}

output "lambda_function_last_modified" {
  description = "The date Lambda Function resource was last modified"
  value       = module.sample_lambda.lambda_function_last_modified
}

output "lambda_function_source_code_hash" {
  description = "Base64-encoded representation of raw SHA-256 sum of the zip file"
  value       = module.sample_lambda.lambda_function_source_code_hash
}

# IAM Role
output "lambda_role_arn" {
  description = "The ARN of the IAM role created for the Lambda Function"
  value       = module.sample_lambda.lambda_role_arn
}

output "lambda_role_name" {
  description = "The name of the IAM role created for the Lambda Function"
  value       = module.sample_lambda.lambda_role_name
}

# CloudWatch Log Group
output "lambda_cloudwatch_log_group_arn" {
  description = "The ARN of the Cloudwatch Log Group"
  value       = module.sample_lambda.lambda_cloudwatch_log_group_arn
}
