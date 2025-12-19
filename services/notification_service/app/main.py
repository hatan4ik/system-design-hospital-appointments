import asyncio
import json
import redis.asyncio as redis
from fastapi import FastAPI
from . import config

app = FastAPI(title='notification-service')

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(subscribe_to_appointments())

async def subscribe_to_appointments():
    r = redis.from_url(config.settings.REDIS_URL, decode_responses=True)
    async with r.pubsub() as pubsub:
        await pubsub.subscribe("appointments")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                print(f"Received message: {message['data']}")

@app.get('/healthz')
def healthz(): 
    return {'ok': True}
