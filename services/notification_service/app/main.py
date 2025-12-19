from fastapi import FastAPI
from . import config

app = FastAPI(title='notification-service')

@app.get('/healthz')
def healthz(): 
    return {'ok': True}