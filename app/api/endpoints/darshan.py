from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Request, Query
from starlette.authentication import requires

from app.core.models.Darshan import Darshan
from app.core.models.User import User
from app.core.schemas.Darshan import (
    DarshanCreate,
    DarshanUpdate,
    DarshanResponse,
    DarshanListResponse,
    DarshanStatus,
    DarshanLeadApprovalUpdate
)

router = APIRouter()

@router.post("", response_model=DarshanResponse)
async def create_darshan_request(
    request: Request,
    darshan_request: DarshanCreate
) -> DarshanResponse:
    """
    Create a new darshan request.
    """
    # Verify if the lead exists and is actually a lead
    lead = await User.find_one(User.userName == darshan_request.leadId, User.role == "lead")
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selected lead not found"
        )

    darshan = Darshan(
        **darshan_request.dict(),
        status=DarshanStatus.PENDING_LEAD
    )
    await darshan.insert()
    return darshan


@router.get("/accepted-darshan", response_model=DarshanListResponse)
async def get_darshan_requests(
) -> DarshanListResponse:
    """
    Get darshan requests based on user role:
    - Leads: see requests assigned to them
    - PAs: see requests approved by leads
    - Admins: see all requests
    """
    query = {}
    query["status"] = "A3"

    total = await Darshan.find(query).count()
    requests = await Darshan.find(query).to_list()
    
    return DarshanListResponse(total=total, items=requests)

@router.get("", response_model=DarshanListResponse)
@requires("authenticated")
async def get_darshan_requests(
    request: Request,
    status: Optional[DarshanStatus] = None
) -> DarshanListResponse:
    """
    Get darshan requests based on user role:
    - Leads: see requests assigned to them
    - PAs: see requests approved by leads
    - Admins: see all requests
    """
    query = {}
    
    if request.user.role == "lead":
        query["leadId"] = request.user.userId
    elif request.user.role == "pa":
        query["status"] = DarshanStatus.PENDING_PA
    
    if status:
        query["status"] = status

    total = await Darshan.find(query).count()
    requests = await Darshan.find(query).to_list()
    
    return DarshanListResponse(total=total, items=requests)

@router.get("/{request_id}", response_model=DarshanResponse)
@requires("authenticated")
async def get_darshan_request(
    request: Request,
    request_id: str
) -> DarshanResponse:
    """
    Get a specific darshan request.
    """
    darshan_request = await Darshan.find_one(Darshan.id == request_id)
    if not darshan_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Darshan request not found"
        )
    
    # Check if user has permission to view this request
    if request.user.role == "lead" and darshan_request.leadId != request.user.userId:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request"
        )
    
    return darshan_request

@router.put("/{request_id}/lead-action", status_code=204)
@requires("authenticated")
async def lead_action(
    request: Request,
    request_id: str,
    action: DarshanLeadApprovalUpdate
):
    """
    Lead can approve or reject the darshan request.
    """
    if request.user.role != "lead":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only leads can perform this action"
        )

    darshan_request = await Darshan.find_one(Darshan.id == request_id, Darshan.leadId == request.user.userId)
    if not darshan_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Darshan request not found"
        )

    if darshan_request.status != DarshanStatus.PENDING_LEAD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot perform action on request with status {darshan_request.status}"
        )
    if action.status == True:
        status = "A2"
    else:
        status = "A4"

    update_data = {
        "status": status,
        "updatedAt": datetime.utcnow(),
        "reason": action.reason
    }

    await darshan_request.set(update_data)

@router.put("/{request_id}/pa-action", status_code=204)
@requires("authenticated")
async def pa_action(
    request: Request,
    request_id: str,
    action: DarshanUpdate
):
    """
    PA can approve (with schedule) or reject the darshan request.
    """
    if request.user.role != "pa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only PAs can perform this action"
        )

    darshan_request = await Darshan.find_one(Darshan.id == request_id)
    if not darshan_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Darshan request not found"
        )

    if darshan_request.status != "A2":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot perform action on request with status {darshan_request.status}"
        )
    
    if action.status == True:
        status = "A3"
    else:
        status = "A4"

    update_data = {
        "status": status,
        "updatedAt": datetime.utcnow(),
        "reason": action.reason
    }
    
    if action.status == True:
        if not action.scheduledDateTime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled date and time is required for approval"
            )
        if not action.scheduledLocation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled location is required for approval"
            )
        update_data["scheduledDateTime"] = action.scheduledDateTime
        update_data["scheduledLocation"] = action.scheduledLocation

    await darshan_request.set(update_data)

@router.delete("/{request_id}")
@requires("authenticated")
async def delete_darshan_request(
    request: Request,
    request_id: str
) -> dict:
    """
    Delete a darshan request. Only admins can delete it.
    """
    if request.user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete darshan requests"
        )

    darshan_request = await Darshan.find_one(Darshan.id == request_id)
    if not darshan_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Darshan request not found"
        )

    await darshan_request.delete()
    return {"message": "Darshan request deleted successfully"}
