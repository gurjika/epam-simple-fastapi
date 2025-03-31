from fastapi import FastAPI
import requests
from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.params import Body
from pydantic import BaseModel
from . import models
from app.db import engine, get_db
from sqlalchemy.orm import Session
from .schemas import PostCreate, PostResponse
 


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
    