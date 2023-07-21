resource "cloudflare_record" "sample_subdomain" {
  zone_id = data.cloudflare_zone.this.id
  name    = var.subdomain
  type    = "CNAME"
  value   = module.api_gateway.apigatewayv2_domain_name_target_domain_name
  ttl     = 300
  proxied = false
}

resource "cloudflare_record" "validation" {
  count = length(module.acm.distinct_domain_names)

  zone_id = data.cloudflare_zone.this.id
  name    = element(module.acm.validation_domains, count.index)["resource_record_name"]
  type    = element(module.acm.validation_domains, count.index)["resource_record_type"]
  value   = trimsuffix(element(module.acm.validation_domains, count.index)["resource_record_value"], ".")
  ttl     = 60
  proxied = false

  allow_overwrite = true
}

module "acm" {
  source = "terraform-aws-modules/acm/aws"

  zone_id                   = data.cloudflare_zone.this.id
  domain_name               = "${var.subdomain}.${var.domain}"
  subject_alternative_names = ["*.${var.subdomain}.${var.domain}"]

  create_route53_records  = false
  validation_record_fqdns = cloudflare_record.validation[*].hostname
}
