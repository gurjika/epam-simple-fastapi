import random
import requests
from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, status
from fastapi.params import Body
from pydantic import BaseModel
from . import models
from app.db import engine, get_db
from sqlalchemy.orm import Session
from .schemas import PostCreate, PostResponse
import boto3
from botocore.exceptions import NoCredentialsError

 
s3 = boto3.client("s3")
AWS_BUCKET_NAME = 'epam-task-bucket-1'
FOLDER_NAME = "uploads/"


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def validate_post(post):
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='post not found')



@app.get('/posts', response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post('/posts', response_model=PostResponse)
def create_posts(post: PostCreate, db: Session = Depends(get_db)):
    posts_dict = post.model_dump()
    new_post = models.Post(**posts_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get('/posts/{id}',  response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    validate_post(post)
    return post


@app.delete('/posts/{id}', response_model=PostResponse)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    validate_post(post.first())
    post.delete()
    db.commit()
    
    return post


@app.put('/posts/{id}', response_model=PostResponse)
def update_post(post: PostCreate, id: int, db: Session = Depends(get_db)):
    update_post_query = db.query(models.Post).filter(models.Post.id == id)
    update_post = update_post_query.first()
    validate_post(update_post)
    
    update_post_query.update(post.model_dump())
    db.commit()
    
    db.refresh(update_post)
    return update_post


@app.get('/home')
def get_home():
    return {"detail": "EC2 seems to Work FINE NOw"}

def get_session_token():
    url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}
    response = requests.put(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print("Error getting session token:", response.status_code)
        return None

def get_metadata(token, metadata_path):
    url = f"http://169.254.169.254/latest/meta-data/{metadata_path}"
    headers = {"X-aws-ec2-metadata-token": token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error getting metadata for {metadata_path}: {response.status_code}")
        return None

@app.get('/info')
def main():
    token = get_session_token()
    if token:
        region = get_metadata(token, "placement/region")

        availability_zone = get_metadata(token, "placement/availability-zone")
        return {"Availability Zone": availability_zone, "Region": region}
    


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_path = FOLDER_NAME + file.filename
        s3.upload_fileobj(file.file, AWS_BUCKET_NAME, file_path)
        
        metadata = models.ImageMetadata(
            filename=file_path,
            content_type=file.content_type,
            size=file.size
        )
        db.add(metadata)
        db.commit()
        db.refresh(metadata)

        return {"message": "File uploaded successfully", "filename": file_path}
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Invalid AWS credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
def download_image(filename: str):
    try:
        file_path = FOLDER_NAME + filename
        url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": AWS_BUCKET_NAME, "Key": file_path}, ExpiresIn=3600
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata/{filename}")
def get_metadata(filename: str, db: Session = Depends(get_db)):
    try:
        file_path = FOLDER_NAME + filename
        metadata = db.query(models.ImageMetadata).filter(models.ImageMetadata.filename == file_path).first()
        if metadata is None:
            raise HTTPException(status_code=404, detail="Metadata not found in database")
        return {"metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata/random")
def get_random_metadata(db: Session = Depends(get_db)):
    try:
        metadata_list = db.query(models.ImageMetadata).all()
        if not metadata_list:
            raise HTTPException(status_code=404, detail="No metadata found in database")
        random_metadata = random.choice(metadata_list)
        return {"filename": random_metadata.filename, "metadata": random_metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/{filename}")
def delete_image(filename: str, db: Session = Depends(get_db)):
    try:
        file_path = FOLDER_NAME + filename
        s3.delete_object(Bucket=AWS_BUCKET_NAME, Key=file_path)
        
        metadata = db.query(models.ImageMetadata).filter(models.ImageMetadata.filename == file_path).first()
        if metadata:
            db.delete(metadata)
            db.commit()
        
        return {"message": "File and metadata deleted successfully", "filename": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
