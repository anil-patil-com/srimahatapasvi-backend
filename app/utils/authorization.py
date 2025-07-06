import time
from typing import Dict
from app.config import settings
import jwt


def tokenResponse(token: str, userId: str, role: str):
    return {"userId": userId, "accessToken": token, "role": role}


# function used for signing the JWT string
def signJWT(userId: str, userRole: str) -> Dict[str, str]:
    payload = {
        "userId": userId,
        "userRole": userRole,
        "expires": time.time() + (24*60*60),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return tokenResponse(token, userId, userRole)


def decodeJWT(token: str) -> dict:
    try:
        decodedToken = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return decodedToken if decodedToken["expires"] >= time.time() else None
    except Exception as error:
        return {}