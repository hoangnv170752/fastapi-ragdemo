from typing import Union
import pandas as pd
from uuid import uuid4
import boto3
from botocore.exceptions import ClientError
import magic
import uvicorn
from fastapi import FastAPI, HTTPException, Response, UploadFile, status
from loguru import logger
import os
from dotenv import load_dotenv

df=pd.read_csv(r"/Users/akashi/Desktop/fastapi-ragdemo/uszips.csv")
app = FastAPI()
load_dotenv()

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf'
}

AWS_BUCKET = os.getenv("AWS_BUCKET")
ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")


s3 = boto3.resource('s3')
bucket = s3.Bucket(AWS_BUCKET)

async def s3_upload(contents: bytes, key: str):
    logger.info('uploading {key} to bucket s3')
    bucket.put_object(Key = key, Body = contents)

async def s3_download(key: str):
    try:
        return s3.Object(bucket_name=AWS_BUCKET, key=key).get()['Body'].read()
    except ClientError as err:
        logger.error(str(err))

session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

@app.get('/')
async def home():
    return {'message': 'Hello from file-upload 😄👋'}

@app.post('/upload')
async def upload(file: UploadFile | None = None):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='where is my file?'
        )
    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 1 * MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Supported file size is 0 - 1 MB'
        )

    file_type = magic.from_buffer(buffer=contents, mime=True)
    if file_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}'
        )
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}'
    await s3_upload(contents=contents, key=file_name)
    return {'file_name': file_name}

# @app.get("/getzip/{name}")
# def getZip(name):
#     df1=df[df["city"]==name]
#     data=str(df1["zip"].values[0])
#     print(df1)
#     return {"Zipcode": "00"+data}

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)