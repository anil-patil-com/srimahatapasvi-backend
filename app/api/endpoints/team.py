from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from starlette.authentication import requires
from app.utils.s3 import upload_file, delete_file, get_presigned_url
from fastapi.openapi.models import Response

from app.core.models.TeamMember import TeamMember
from app.core.schemas.TeamMember import (
    TeamMemberResponse, TeamMemberListResponse
)

router = APIRouter()

@router.post("", response_model=TeamMemberResponse)
@requires("authenticated")
async def createTeamMember(
    request: Request,
    name: str = Form(..., description="Name of the team member"),
    role: str = Form(..., description="Role of the team member"),
    description: str = Form(..., description="Description of the team member"),
    image: UploadFile = File(..., description="Profile image of the team member")
) -> TeamMemberResponse:
    """
    Create a new team member with the following data:
    - name: Name of the team member
    - role: Role/position of the team member
    - description: Detailed description about the team member
    - image: Profile image file (supported formats: JPG, PNG)
    """
    try:
        # Upload image
        imageKey = await upload_file(image, "team")

        # Create team member
        team_member = await TeamMember(
            id=str(uuid4()),
            name=name,
            role=role,
            description=description,
            image=imageKey,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        ).save()

        # Add presigned URL for response
        response_member = team_member.dict()
        response_member["image"] = get_presigned_url(imageKey)
        
        return response_member
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("", response_model=TeamMemberListResponse)
async def getTeamMembers() -> TeamMemberListResponse:
    """
    Get a list of team members with pagination support.
    """
    total = await TeamMember.find().count()
    team_members = await TeamMember.find().to_list()
    
    # Add presigned URLs for response
    response_members = []
    for member in team_members:
        member_dict = member.dict()
        member_dict["image"] = get_presigned_url(member.image)
        response_members.append(member_dict)
    
    return TeamMemberListResponse(total=total, items=response_members)

@router.get("/{member_id}", response_model=TeamMemberResponse)
async def getTeamMember(member_id: str) -> TeamMemberResponse:
    """
    Get a specific team member by their ID.
    """
    team_member = await TeamMember.find_one(TeamMember.id == member_id)
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )
    
    # Add presigned URL for response
    response_member = team_member.dict()
    response_member["image"] = get_presigned_url(team_member.image)
    
    return response_member

@router.put("/{member_id}", response_model=TeamMemberResponse)
@requires("authenticated")
async def updateTeamMember(
    request: Request,
    member_id: str,
    name: Optional[str] = Form(None, description="Updated name of the team member"),
    role: Optional[str] = Form(None, description="Updated role of the team member"),
    description: Optional[str] = Form(None, description="Updated description of the team member"),
    image: UploadFile = File(None, description="Updated profile image file (JPG, PNG)")
) -> TeamMemberResponse:
    """
    Update an existing team member. All fields are optional:
    - name: Updated name of the team member
    - role: Updated role/position
    - description: Updated description
    - image: New profile image file (supported formats: JPG, PNG)
    """
    try:
        team_member = await TeamMember.find_one(TeamMember.id == member_id)
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team member with ID {member_id} not found"
            )

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if role is not None:
            update_data["role"] = role
        if description is not None:
            update_data["description"] = description

        # Handle image update
        if image and image.filename:
            # Delete old image if it exists
            if team_member.image:
                await delete_file(team_member.image)
            
            # Upload new image
            imageKey = await upload_file(image, "team")
            update_data["image"] = imageKey

        update_data["updatedAt"] = datetime.utcnow()
        await team_member.update({"$set": update_data})
        
        # Get updated member
        updated_member = await TeamMember.find_one(TeamMember.id == member_id)
        
        # Add presigned URL for response
        response_member = updated_member.dict()
        response_member["image"] = get_presigned_url(updated_member.image)
        
        return response_member
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{member_id}")
@requires("authenticated")
async def deleteTeamMember(
    request: Request,
    member_id: str
) -> dict:
    """
    Delete a team member by their ID. This will also delete their profile image from storage.
    """
    team_member = await TeamMember.find_one(TeamMember.id == member_id)
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with ID {member_id} not found"
        )

    # Delete image if it exists
    if team_member.image:
        delete_file(team_member.image)

    await team_member.delete()
    return {"message": "Team member deleted successfully"}
