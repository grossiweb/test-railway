import boto3
from botocore.config import Config
from flask import Flask, jsonify
import os
from dotenv import load_dotenv
load_dotenv()

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=os.environ["AWS_REGION"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
            config=Config(signature_version='s3v4')
        )
        self.BUCKET_NAME = 'los-angelos'

    def get_specific_style(self, gender: str, category: str, filename: str):
        try:
            # Construct the S3 key
            key = f'styles/{gender}/{category}/{filename}'
            
            # Generate a presigned URL that's valid for 1 hour
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.BUCKET_NAME,
                    'Key': key
                },
                ExpiresIn=600
            )

            return url
        except Exception as e:
            print(f"Error fetching style: {str(e)}")
            raise Exception(f"Failed to fetch style: {filename}")
