import json
import os
import boto3
from io import BytesIO
from PIL import Image
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

# Powertools, Logging and Trace
logger = Logger(service="media-processor")
tracer = Tracer(service="media-processor")
metrics = Metrics(namespace="ServerlessMediaProcesing", service="media-processor")

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET")
TABLE_NAME = os.environ.get("TABLE_NAME")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics
def lambda_handler(event, context):
    for record in event: # Not: Genelde event['Records'] olur, kodunuza sadık kaldım.
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        logger.info(f"Processing image: {key} from {bucket}")
        
        try:
            # 1. Resmi S3'ten Çek
            response = s3.get_object(Bucket=bucket, Key=key)
            image_content = response.read() # Boto3 sürümüne göre response['Body'].read() gerekebilir.
            
            logger.info("Image downloaded successfully")

        except Exception as e:
            logger.exception("Error processing image")
            raise e
            
    return {"statusCode": 200, "body": "Success"}