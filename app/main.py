from fastapi import FastAPI
from app.mail import router as mail_router
from app.telegram import router as telegram_router

app = FastAPI(title="Notification API")

app.include_router(mail_router)
app.include_router(telegram_router)
