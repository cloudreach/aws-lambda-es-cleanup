


provider "aws" {
  region = "eu-west-1"

}


module "public_es_cleanup" {
  source       = "giuliocalzolari/es-cleanup/aws"
  # version      = "1.11.0"
  prefix       = "public_es_"
  es_endpoint  = "test-es-XXXXXXX.eu-central-1.es.amazonaws.com"
  delete_after = 365
}