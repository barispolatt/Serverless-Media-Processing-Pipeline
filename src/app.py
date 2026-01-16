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
    for record in event:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        logger.info(f"Processing image: {key} from {bucket}")
        
        try:
            # Pull image from S3
            response = s3.get_object(Bucket=bucket, Key=key)
            image_content = response.read() # Boto3 may need response['Body'].read()
            
            logger.info("Image downloaded successfully")

            # Modifiy with Rekognition (Violence/Nudity Scanning)
            rekog_response = rekognition.detect_moderation_labels(
                Image={'Bytes': image_content},
                MinConfidence=70
            )
            labels = rekog_response['ModerationLabels']
            logger.info(f"Rekognition Labels: {json.dumps(labels)}")
            
            unsafe_content = len(labels) > 0

            if not unsafe_content:
                image = Image.open(BytesIO(image_content))
                image.thumbnail((1024, 1024)) # Resize
                buffer = BytesIO()
                image.save(buffer, "JPEG")
                buffer.seek(0)
                
                s3.put_object(
                    Bucket=OUTPUT_BUCKET,
                    Key=f"processed/{key}",
                    Body=buffer,
                    ContentType='image/jpeg'
                )
                logger.info("Image resized and saved.")
            else:
                logger.warn("Unsafe content detected! Skipping resize.")
                # Inform the Admin with SNS
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=f"Warning: Unsafe content detected in {key}. Labels: {labels}",
                    Subject="Content Moderation Alert"
                )
        except Exception as e:
            logger.exception("Error processing image")
            raise e
            
    return {"statusCode": 200, "body": "Success"}