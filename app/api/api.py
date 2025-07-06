from fastapi import APIRouter

from app.api.endpoints import auth, events, spiritual_events, team, darshan

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
api_router.include_router(spiritual_events.router, prefix="/spiritual-events", tags=["Spiritual Events"])
api_router.include_router(team.router, prefix="/team", tags=["Team"])
api_router.include_router(darshan.router, prefix="/darshan", tags=["Darshan Requests"])
