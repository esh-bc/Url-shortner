from fastapi import FastAPI
import uvicorn
import threading

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "Bot is running!"}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}


def run():
    uvicorn.run(app, host="0.0.0.0", port=8080)


def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
