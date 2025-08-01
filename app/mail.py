from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from itsdangerous import URLSafeSerializer
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from app.config import *

router = APIRouter()
serializer = URLSafeSerializer(EMAIL_SECRET)

class EmailRequest(BaseModel):
    email: EmailStr
    reservation: dict  # contains reservation_id, flat_type, plan, total_price, date, time

class DeclineTokenRequest(BaseModel):
    token: str

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/send-email")
def send_email(payload: EmailRequest):
    try:
        data = payload.reservation
        token = serializer.dumps(data["reservation_id"])
        decline_url = f"https://staging.raccoon.bg/api/reservations/decline?token={token}"

        html = f"""
        <html>
          <body>
            <h3>Благодарим Ви за заявката!</h3>
            <p>Тип апартамент: {data['flat_type']}</p>
            <p>План: {data.get('plan', 'Потребителски')}</p>
            <p>Обща цена: {data['total_price']} лв</p>
            <p>Желана дата: {data.get('date', '')}</p>
            <p>Час: {data.get('time', '')}</p>
            <br>
            <a href="{decline_url}" style="padding: 10px 20px; background: #e00; color: white; text-decoration: none;">Откажи заявката</a>
          </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Заявка за почистване - Raccoon Cleaning"
        msg["From"] = SMTP_SENDER
        msg["To"] = payload.email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER, [payload.email], msg.as_string())

        return {"status": "sent"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-decline-token")
def verify_token(req: DeclineTokenRequest):
    try:
        reservation_id = serializer.loads(req.token)
        return {"reservation_id": reservation_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/send-contact")
def send_contact_email(msg: ContactMessage):
    try:
        receiver = "kmerev.raccoon@gmail.com"
        html = f"""
        <html>
          <body>
            <h4>Ново съобщение от контактната форма</h4>
            <p><strong>Име:</strong> {msg.name}</p>
            <p><strong>Email за връзка:</strong> {msg.email}</p>
            <p><strong>Съобщение:</strong></p>
            <p>{msg.message}</p>
          </body>
        </html>
        """

        mime = MIMEMultipart("alternative")
        mime["Subject"] = "Ново запитване от сайта"
        mime["From"] = SMTP_SENDER
        mime["To"] = receiver
        mime.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_SENDER, receiver, mime.as_string())

        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
