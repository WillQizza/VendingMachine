from contextlib import asynccontextmanager

from fastapi import FastAPI

from vending_machine.ai.config import load_settings
from vending_machine.api.router import router
from vending_machine.conversations import ConversationManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    app.state.conversation_manager = ConversationManager(currency=settings.currency)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
