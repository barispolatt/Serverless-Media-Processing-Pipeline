provider "aws" {
  region = "us-west-2" # Oregon
}
variable "project_name" { default = "serverlessmediaprocesing-demo" }

resource "random_id" "bucket_suffix" { byte_length = 4 }

# S3 Buckets
resource "aws_s3_bucket" "input" {
  bucket = "${var.project_name}-input-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket" "output" {
  bucket = "${var.project_name}-output-${random_id.bucket_suffix.hex}"
  force_destroy = true
}


