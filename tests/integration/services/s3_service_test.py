from http import HTTPStatus

import pytest
import requests
from django.conf import settings

from app.internal.domain.services.s3_service import S3Service

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


@pytest.fixture
def s3():
    return S3Service()


@pytest.fixture
def bucket(s3):
    s3.client.create_bucket(Bucket=settings.S3_BUCKET)
    yield
    s3.client.delete_bucket(Bucket=settings.S3_BUCKET)


@pytest.fixture
def file(s3, bucket):
    s3.client.put_object(Body="aboba", Bucket=settings.S3_BUCKET, Key="file.txt")
    yield "file.txt"
    s3.client.delete_object(Bucket=settings.S3_BUCKET, Key="file.txt")


async def test_create_presigned_url(s3, file):
    url = await s3.create_presigned_url(file)
    response = requests.get(url)
    assert response.status_code == HTTPStatus.OK
    assert response.text == "aboba"
