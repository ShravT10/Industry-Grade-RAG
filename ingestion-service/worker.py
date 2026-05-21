# worker.py
import os
import json
import time
import boto3
import tempfile
import asyncio
from app.ingestion.pipeline import ingest_pdf_async
from app.ssl_patch import apply_patch
from dotenv import load_dotenv

load_dotenv()
apply_patch()

sqs = boto3.client(
    "sqs",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

QUEUE_URL = os.getenv("SQS_QUEUE_URL")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def process_message(message):
    body = json.loads(message["Body"])

    # S3 event notification format
    records = body.get("Records", [])

    for record in records:
        s3_key = record["s3"]["object"]["key"]
        file_name = os.path.basename(s3_key)

        print(f"Processing file: {s3_key}")

        # Download from S3 to a temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            s3.download_file(BUCKET_NAME, s3_key, tmp_path)
            print(f"Downloaded {file_name} from S3")

            asyncio.run(ingest_pdf_async(tmp_path, file_name))

            # Move to processed/ prefix after success
            processed_key = s3_key.replace("uploads/", "processed/")
            s3.copy_object(
                Bucket=BUCKET_NAME,
                CopySource={"Bucket": BUCKET_NAME, "Key": s3_key},
                Key=processed_key
            )
            s3.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
            print(f"Moved {file_name} to processed/")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def poll():
    print("Worker started — polling SQS...")

    while True:
        try:
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,        # one at a time — safe for large PDFs
                WaitTimeSeconds=20,           # long polling — cheaper than short polling
                VisibilityTimeout=300         # 5 min — time allowed to process before retry
            )

            messages = response.get("Messages", [])

            if not messages:
                print("No messages — waiting...")
                continue

            for message in messages:
                try:
                    process_message(message)

                    # Delete from SQS only after successful processing
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message["ReceiptHandle"]
                    )
                    print("Message deleted from SQS")

                except Exception as e:
                    print(f"Error processing message: {e}")
                    # Don't delete — SQS will retry after VisibilityTimeout
                    # After max retries it goes to DLQ automatically

        except Exception as e:
            print(f"SQS polling error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    poll()


#HIEEE
