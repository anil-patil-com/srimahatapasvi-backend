from typing import Optional, Tuple
from starlette.authentication import AuthenticationBackend, AuthenticationError, AuthCredentials, BaseUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from jose import JWTError, jwt

from app.core.models.User import User
from app.utils.constants import USER_NOT_FOUND, INVALID_CREDENTIALS
from app.config import settings
from app.utils.constants import AuthConstants
from app.utils.authorization import decodeJWT
import re

rules = {
    "GET": {
        "/v1/.*": [AuthConstants.ADMIN_ROLE]
    },
    "POST": {
        "/v1/.*": [AuthConstants.ADMIN_ROLE]
    },
    "PUT": {
        "/v1/.*": [AuthConstants.ADMIN_ROLE]
    },
    "PATCH": {
        "/v1/.*": [AuthConstants.ADMIN_ROLE]
    },
    "DELETE": {
        "/v1/.*": [AuthConstants.ADMIN_ROLE]
    }
}

class AuthenticatedUser:
    userId: str
    role: str

    def __init__(self, userId, role) -> None:
        self.userId = userId
        self.role = role


def getRoleForMatchingRule(method, apiPath):
    methodRules = rules.get(method, {})
    roles = []
    for path, role in methodRules.items():
        if re.fullmatch(path, apiPath):
            roles.extend(role)
    return roles


def userAuthentication(conn):
    token = conn.headers.get(AuthConstants.AUTHORIZATION, AuthConstants.EMPTY_STRING)
    method = conn.__dict__.get(AuthConstants.SCOPE, {}).get(AuthConstants.METHOD, {})
    path = conn.__dict__.get(AuthConstants.SCOPE, {}).get(AuthConstants.PATH, {})
    decodedToken = decodeJWT(token)
    if decodedToken != {} or decodedToken is not None:
        userId = decodedToken.get(AuthConstants.USER_ID, AuthConstants.EMPTY_STRING)
        userRole = decodedToken.get(AuthConstants.USER_ROLE, AuthConstants.EMPTY_STRING)
        return AuthCredentials([AuthConstants.AUTHENTICATED]), AuthenticatedUser(
            userId, userRole
        )
    else:
        return AuthCredentials([]), None

class ApiAuthBackend(AuthenticationBackend):
    skipAuthentication: bool
    skipTestAuthentication: bool

    def __init__(self, skipAuthentication=False, skipTestAuthentication=True) -> None:
        self.skipAuthentication = skipAuthentication
        self.skipTestAuthentication = skipTestAuthentication

    async def authenticate(self, conn):
        if self.skipAuthentication:
            return AuthCredentials([AuthConstants.AUTHENTICATED]), AuthenticatedUser(
                AuthConstants.ADMIN, AuthConstants.ADMIN
            )
        else:
            return userAuthentication(conn)
