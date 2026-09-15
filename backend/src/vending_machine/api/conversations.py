"""Streaming HTTP routes for vending-machine conversations."""

from collections.abc import Iterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from vending_machine.api.schemas import ConversationCreated, ConversationMessage
from vending_machine.conversations import ConversationManager, ConversationNotFoundError


router = APIRouter()


@router.post(
    "/conversations",
    response_model=ConversationCreated,
    status_code=status.HTTP_201_CREATED,
)
def start_conversation(request: Request) -> ConversationCreated:
    manager = _get_conversation_manager(request)
    try:
        conversation_id = manager.start_conversation()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The OpenAI provider is unavailable.",
        ) from exc
    return ConversationCreated(conversation_id=conversation_id)


@router.post("/conversations/{conversation_id}/messages")
def send_message(
    conversation_id: str,
    message: ConversationMessage,
    request: Request,
) -> StreamingResponse:
    manager = _get_conversation_manager(request)
    try:
        manager.get_conversation(conversation_id)
    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        ) from exc

    return StreamingResponse(
        _stream_response(manager, conversation_id, message.content),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _get_conversation_manager(request: Request) -> ConversationManager:
    return request.app.state.conversation_manager


def _stream_response(
    manager: ConversationManager,
    conversation_id: str,
    content: str,
) -> Iterator[str]:
    try:
        yield from manager.stream_message(conversation_id, content)
    except Exception:
        yield "event: error\ndata: {\"detail\": \"The conversation could not be completed.\"}\n\n"
