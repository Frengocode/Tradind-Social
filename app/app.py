from fastapi import FastAPI
from src.signals_service.api import signal_service
from src.user_service.api import user_service_router
from src.config.user_database import UserBS, user_engine
from src.config.signals_database import signal_engine, SignalBASE
from src.config.view_database import ViewBASE, view_engine
from src.config.news_database import NewsBASE, news_engine
from src.config.comment_database import comment_engine, CommentBase
from src.auth_service.api import auth_service
from fastapi.middleware.cors import CORSMiddleware
from src.graphy_service.api import graphy_service
from src.view_service.api import view_service_router
from src.news_service.api import news_service_router
from src.comment_service.api import comment_service_router




app = FastAPI(title="Trading Social Media App")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(signal_service)
app.include_router(user_service_router)
app.include_router(auth_service)
app.include_router(graphy_service)
app.include_router(view_service_router)
app.include_router(news_service_router)
app.include_router(comment_service_router)


async def create_tables():
    async with user_engine.begin() as conn:
        await conn.run_sync(UserBS.metadata.create_all)

    async with signal_engine.begin() as conn:
        await conn.run_sync(SignalBASE.metadata.create_all)

    async with view_engine.begin() as conn:
        await conn.run_sync(ViewBASE.metadata.create_all)

    async with news_engine.begin() as conn:
        await conn.run_sync(NewsBASE.metadata.create_all)

    async with comment_engine.begin() as conn:
        await conn.run_sync(CommentBase.metadata.create_all)



@app.on_event("startup")
async def create_tables_():
    return await create_tables()