from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .commands import router as commands_router


app = FastAPI(title="RemoteOC", description="RemoteOC的服务端", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(commands_router, prefix="/api/cmd")
