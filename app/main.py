from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)


while True:
    try:
        conn = psycopg2.connect(host='localhost', port=5432, database='fastapi',
                                user='postgres', password="KAKAmama", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("database connection established")
        break
    except Exception as e:
        print("database connection failed")
        print("error : " + str(e))
        time.sleep(2)

app = FastAPI()

my_post = [{'title': 'title of the post 1', 'content': 'content of the post 1', 'id': 1},
           {'title': 'title of the post 2',
               'content': 'content of the post 2', 'id': 2}
           ]


def find_post(id):
    for p in my_post:
        if p['id'] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_post):
        if p['id'] == id:
            return i


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


@app.get("/")
async def root():
    print('root done')
    return {"message": "Hello, world!"}


@app.get("/posts")
async def get_posts():
    cursor.execute(""" select * from posts """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def crete_posts(post: Post):
    cursor.execute(""" insert into posts (title, content, published) values(%s, %s, %s) returning *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.get("/posts/{id}")
async def get_post(id: int, response: Response):

    cursor.execute(""" select * from posts where id = {id}""")
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    return {"post_details": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int):
    try:
        cursor.execute("DELETE FROM posts WHERE id = {id}")
        conn.commit()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
async def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    post_dict = post.dict()
    post_dict['id'] = id
    my_post[index] = post_dict
    return {"message": 'Update post'}
