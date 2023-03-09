from fastapi import APIRouter, HTTPException, status

from src.config import producer
from src.schemas import Message
from src.settings import settings

router = APIRouter()


@router.post("/publish/",
             openapi_extra={"x-request-id": "request ID"},
             status_code=status.HTTP_200_OK)
async def publish(message: Message):
    try:
        return await producer.publish(queue_name=settings.QUEUE_NAME, message=message.dict())
    except RuntimeError:
        await producer.connect_broker()
        return await producer.publish(queue_name=settings.QUEUE_NAME, message=message.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
