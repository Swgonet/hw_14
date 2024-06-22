from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fast_api_app.routes import users, auth
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio

app = FastAPI()
origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, like databases or caches.

    :return: A list of functions that will be called after the server starts
    :doc-author: Trelent
    """
    r = await redis.asyncio.Redis(host='localhost', port=6379, db=0, encoding="utf-8",
                                  decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Hello World"}
