from fastapi import APIRouter, HTTPException, status

from src.config import producer
from src.schemas import Message

router = APIRouter()


@router.post("/publish/")
async def publish(message: Message):
    try:
        return await producer.publish(queue_name="email", message=message.dict())
    except RuntimeError:
        await producer.connect_broker()
        return await producer.publish(queue_name="email", message=message.dict())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
