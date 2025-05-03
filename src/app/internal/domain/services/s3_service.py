from io import BytesIO
from uuid import uuid4

from boto3 import client
from botocore.client import Config
from django.conf import settings


class S3Service:
    def __init__(self):
        self.client = client(
            "s3",
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
        )

    async def upload_image(self, file: bytearray) -> str:
        file_id = f"{uuid4()}.png"
        self.client.put_object(Bucket=settings.S3_BUCKET, Key=file_id, Body=BytesIO(file))
        return file_id

    async def create_presigned_url(self, object_name: str, expiration: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": object_name},
            HttpMethod="GET",
            ExpiresIn=expiration,
        )
