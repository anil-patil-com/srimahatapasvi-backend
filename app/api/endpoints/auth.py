from starlette.authentication import requires
from typing import List
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Request
from app.core.models.User import User
from app.core.schemas.User import UserCreate, UserResponse, TokenPayload, Token, UserLogin
from app.config import settings
from app.utils.authorization import signJWT

router = APIRouter()

@router.post("/register", response_model=UserResponse)
@requires("authenticated")
async def register(user_in: UserCreate, request: Request) -> UserResponse:
    """
    Register a new user.
    """
    # Check if username already exists
    if await User.find_one(User.userName == user_in.userName):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    user = User(
        id=str(uuid4()),
        name=user_in.name,
        userName=user_in.userName,
        role=user_in.role,
        phoneNumber=user_in.phoneNumber,
        password=user_in.password,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    await user.insert()
    return user

@router.get("/users", response_model=List[UserResponse])
async def getUsers():
    users = await User.find().to_list()
    usersList = []
    for user in users:
        usersList.append(user.dict())
    return usersList

@router.get("/leads", response_model=list[dict])
async def getLeads():
    leads = await User.find(User.role == "lead").to_list()
    leadIds = []
    for lead in leads:
        lead = lead.dict()
        leadIds.append({'id':lead['userName'],'name':lead['name']})
    return leadIds

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await User.find_one(User.userName == user_in.userName)
    if not user or user.password != user_in.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = signJWT(userId=user.userName, userRole=user.role)

    return token