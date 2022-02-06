from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import time

app = FastAPI()

class Post(BaseModel):
  title: str
  content: str
  published: Optional[bool] = True


while True:
  try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Joshua1234', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print('Database connected.')
    break
  except Exception:
    print('Connection Failed, trying again')
    time.sleep(2)

my_posts = []

@app.get('/posts')
def get_posts():
  cursor.execute('SELECT * FROM posts')
  posts = cursor.fetchall()
  return {'data': posts}

@app.post('/posts', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
  cursor.execute(f'INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *', (post.title, post.content, post.published))
  new_posts = cursor.fetchone()
  conn.commit()
  return {'data': new_posts}

@app.get('/posts/latest')
def get_latest_post():
  post = my_posts[len(my_posts)-1]
  return post

@app.get('/posts/{id}')
def get_posts_by_id(id: int, response: Response):
  cursor.execute('SELECT * FROM posts WHERE id = %s', str(id))
  post = cursor.fetchone()
  if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} was not found')

  return {'data': post}

@app.delete('/posts/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
  cursor.execute('DELETE FROM posts WHERE id = %s RETURNING *', str(id))
  deleted_post = cursor.fetchone() 
  conn.commit()
  
  if deleted_post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} was not found')

  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/posts/{id}')
def update_post(id: int, post: Post):
  cursor.execute('UPDATE posts SET title = %s, content = %s, published = %s RETURNING *', (post.title, post.content, post.published))
  updated_post = cursor.fetchone()
  conn.commit()

  if updated_post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {id} was not found')

  return {'data': updated_post}


