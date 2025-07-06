from enum import Enum

class EventType(str, Enum):
    HEALTH = "ಆರೋಗ್ಯ"
    DONATION = "ದಾನ"
    EDUCATION = "ಶಿಕ್ಷಣ"
    TRAINING = "ತರಬೇತಿ"
    SPIRITUAL = "ಆಧ್ಯಾತ್ಮಿಕ"

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class AuthConstants:
    ADMIN: str = "admin"
    ADMIN_ROLE: str = "admin"
    AUTHENTICATED: str = "authenticated"
    AUTHORIZATION: str = "Authorization"
    EMPTY_STRING: str = ""
    HOST: str = "host"
    METHOD: str = "method"
    PATH: str = "path"
    SCOPE: str = "scope"
    TEST_CLIENT: str = "test client"
    TEST_CLIENT_TYPE: str = "test client type"
    TEST_CLIENT_ROLE: str = "test client role"
    TEST_SERVER: str = "testserver"
    USER_ID: str = "userId"
    USER_ROLE: str = "userRole"
    USER_TYPE: str = "userType"

# Authentication Constants
TOKEN_TYPE = "bearer"
TOKEN_URL = "/api/auth/login"

# Error Messages
INVALID_CREDENTIALS = "Invalid credentials"
USER_EXISTS = "User with this email already exists"
USER_NOT_FOUND = "User not found"
UNAUTHORIZED = "Could not validate credentials"
FORBIDDEN = "Not enough permissions"
