from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import *
import httpx

router = APIRouter()

class TelegramRequest(BaseModel):
    reservation: dict

@router.post("/send-telegram")
async def send_telegram(payload: TelegramRequest):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=500, detail="Telegram not configured")

    r = payload.reservation
    message = (
        f"📩 *Нова резервация!* - {r['service_type']}\n\n"
        f"👤 *Име:* {r['name']}\n"
        f"📞 *Тел:* {r['phone']}\n"
        f"🏠 *Адрес:* {r['address']}\n"
        f"🏢 *Тип:* {r['flat_type']}\n"
        f"📦 *План:* {r.get('plan', 'Потребителски')}\n"
        f"🧹 *Дейности:* {', '.join(r['activities'])}\n"
        f"💰 *Цена:* {r['total_price']} лв\n"
        f"📅 *Дата:* {r['date']}\n"
        f"🕒 *Час:* {r['time'][:5]}"
    )

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                }
            )
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram failed: {str(e)}")
