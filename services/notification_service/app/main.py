from fastapi import FastAPI
app = FastAPI(title='notification-service')
@app.get('/healthz')
def healthz(): return {'ok': True}
