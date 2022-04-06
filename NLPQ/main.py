from fastapi import FastAPI
from .routers import transactionrouter

app = FastAPI()
app.include_router(transactionrouter)
