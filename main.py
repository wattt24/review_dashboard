# main.py
from fastapi import FastAPI
from routers import oauth_shopee

app = FastAPI()

app.include_router(oauth_shopee.router)
