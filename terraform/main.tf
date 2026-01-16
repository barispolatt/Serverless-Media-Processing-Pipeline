provider "aws" {
  region = "us-west-2" # Oregon
}
variable "project_name" { default = "ServerlessMediaProcesing" }

resource "random_id" "bucket_suffix" { byte_length = 4 }
