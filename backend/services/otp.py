"""OTP код генерациясы мен верификациясы"""
import random
import jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from models import OTPCode
from config import JWT_SECRET


def generate_otp_code(db: Session, phone: str) -> str:
    """4 санды OTP код генерациялау"""
    # Rate limit: 1 минутта 1 рет
    recent = db.query(OTPCode).filter(
        OTPCode.phone == phone,
        OTPCode.created_at > datetime.now() - timedelta(minutes=1),
        OTPCode.is_used == False
    ).first()
    if recent:
        raise ValueError("Кодты 1 минуттан кейін қайта сұраңыз")

    code = str(random.randint(1000, 9999))

    otp = OTPCode(
        phone=phone,
        code=code,
        expires_at=datetime.now() + timedelta(minutes=5),
    )
    db.add(otp)
    db.commit()

    return code


def verify_otp_code(db: Session, phone: str, code: str) -> bool:
    """OTP кодты тексеру"""
    otp = db.query(OTPCode).filter(
        OTPCode.phone == phone,
        OTPCode.code == code,
        OTPCode.is_used == False,
        OTPCode.expires_at > datetime.now()
    ).order_by(OTPCode.created_at.desc()).first()

    if not otp:
        return False

    otp.is_used = True
    db.commit()
    return True


def create_access_token(phone: str) -> str:
    """Қарапайым JWT token жасау (15 мин мерзім)"""
    payload = {
        "phone": phone,
        "exp": datetime.now() + timedelta(minutes=15),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_access_token(token: str) -> Optional[str]:
    """JWT token-ді тексеру, phone қайтару"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("phone")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
