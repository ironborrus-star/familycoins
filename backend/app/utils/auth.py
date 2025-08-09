"""
Утилиты для аутентификации и работы с JWT токенами
"""
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

# Настройки JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_key_change_in_production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Контекст для хеширования паролей (в данном случае - пасскодов)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passcode() -> str:
    """Генерирует 6-значный пасскод для семьи"""
    return f"{secrets.randbelow(900000) + 100000:06d}"


def verify_passcode(plain_passcode: str, hashed_passcode: str) -> bool:
    """Проверяет пасскод"""
    return pwd_context.verify(plain_passcode, hashed_passcode)


def get_passcode_hash(passcode: str) -> str:
    """Хеширует пасскод"""
    return pwd_context.hash(passcode)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль пользователя"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширует пароль пользователя"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Проверяет и декодирует JWT токен"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )