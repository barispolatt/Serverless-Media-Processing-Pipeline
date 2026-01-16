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

# DynamoDB 
resource "aws_dynamodb_table" "metadata" {
  name           = "${var.project_name}-meta"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "image_id"
  attribute {
    name = "image_id"
    type = "S"
  }
}

# SNS 
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
}

# IAM Role (Least Privilege)
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-role"
  
  # Assume Role Policy
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-policy"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Action = ["s3:GetObject"], Effect = "Allow", Resource = "${aws_s3_bucket.input.arn}/*" },
      { Action = ["s3:PutObject"], Effect = "Allow", Resource = "${aws_s3_bucket.output.arn}/*" },
      { Action = ["rekognition:DetectModerationLabels"], Effect = "Allow", Resource = "*" },
      { Action = ["dynamodb:PutItem"], Effect = "Allow", Resource = aws_dynamodb_table.metadata.arn },
      { Action = ["sns:Publish"], Effect = "Allow", Resource = aws_sns_topic.alerts.arn },
      { Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], Effect = "Allow", Resource = "arn:aws:logs:*:*:*" }
    ]
  })
}

# Lambda Function
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "../src" 
  output_path = "lambda_pkg.zip"
}

resource "aws_lambda_function" "processor" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.project_name}-func"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
  memory_size      = 512

  environment {
    variables = {
      OUTPUT_BUCKET           = aws_s3_bucket.output.id
      TABLE_NAME              = aws_dynamodb_table.metadata.name
      SNS_TOPIC_ARN           = aws_sns_topic.alerts.arn
      POWERTOOLS_SERVICE_NAME = "media-processor"
    }
  }
}