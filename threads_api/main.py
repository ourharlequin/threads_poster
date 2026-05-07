from contextlib import asynccontextmanager
from fastapi import FastAPI
import registry
from routers import analytics, content, publishing, system, superset, optimize, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    registry.REGISTRY.update(registry.build_registry())
    yield


app = FastAPI(title="Threads API", version="1.0.0", lifespan=lifespan)

app.include_router(analytics.router,  prefix="/analytics",  tags=["analytics"])
app.include_router(content.router,    prefix="/content",    tags=["content"])
app.include_router(publishing.router, prefix="/publishing", tags=["publishing"])
app.include_router(system.router,     prefix="/system",     tags=["system"])
app.include_router(superset.router,   prefix="/superset",   tags=["superset"])
app.include_router(optimize.router,   prefix="/optimize",   tags=["optimize"])
app.include_router(chat.router,       tags=["chat"])
