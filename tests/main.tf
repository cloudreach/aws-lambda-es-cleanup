terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  region = "eu-central-1"
}


data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "es_management_access" {
  count = false == local.inside_vpc ? 1 : 0

  statement {
    sid = "1"
    actions = [
      "es:*",
    ]

    resources = ["${aws_elasticsearch_domain.es[0].arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

  }

  statement {
    sid = "2"
    actions = [
      "es:*",
    ]

    resources = ["${aws_elasticsearch_domain.es[0].arn}/*"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    condition {
      test     = "IpAddress"
      variable = "aws:SourceIp"

      values = ["${chomp(data.http.myip.body)}/32"]
    }
  }
}

resource "aws_elasticsearch_domain" "es" {
  count = false == local.inside_vpc ? 1 : 0

  depends_on = [aws_iam_service_linked_role.es]

  domain_name           = local.domain_name
  elasticsearch_version = var.es_version

  encrypt_at_rest {
    enabled    = var.encrypt_at_rest
    kms_key_id = var.kms_key_id
  }

  cluster_config {
    instance_type            = var.instance_type
    instance_count           = var.instance_count
    dedicated_master_enabled = var.instance_count >= var.dedicated_master_threshold ? true : false
    dedicated_master_count   = var.instance_count >= var.dedicated_master_threshold ? 3 : 0
    dedicated_master_type    = var.instance_count >= var.dedicated_master_threshold ? var.dedicated_master_type != "false" ? var.dedicated_master_type : var.instance_type : ""
    zone_awareness_enabled   = var.es_zone_awareness
  }

  advanced_options = var.advanced_options

  node_to_node_encryption {
    enabled = var.node_to_node_encryption_enabled
  }

  ebs_options {
    ebs_enabled = var.ebs_volume_size > 0 ? true : false
    volume_size = var.ebs_volume_size
    volume_type = var.ebs_volume_type
  }

  snapshot_options {
    automated_snapshot_start_hour = var.snapshot_start_hour
  }

  tags = merge(
    {
      "Domain" = local.domain_name
    },
    var.tags,
  )
}

resource "aws_elasticsearch_domain_policy" "es_management_access" {
  count = false == local.inside_vpc ? 1 : 0

  domain_name     = local.domain_name
  access_policies = data.aws_iam_policy_document.es_management_access[0].json
}




module "public_es_cleanup" {
  source = "../terraform/"

  prefix       = "public_es_"
  es_endpoint  = element(aws_elasticsearch_domain.es.*.endpoint, 0)
  delete_after = 1
}
