output "api_endpoint" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.frontend_cdn.domain_name
}