from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Request
from starlette.authentication import requires

from app.core.models.Applicant import Applicant
from app.core.schemas.Applicant import ApplicantCreate, ApplicantResponse, ApplicantListResponse

router = APIRouter()


@router.get("", response_model=ApplicantListResponse)
@requires("authenticated")
async def get_all_applicants(request: Request) -> ApplicantListResponse:
    """
    Get all applicants.
    """
    try:
        applicants = await Applicant.find_all().to_list()
        
        applicant_responses = [
            ApplicantResponse(
                id=str(applicant.id),
                name=applicant.name,
                Address=applicant.Address,
                contactNumber=applicant.contactNumber
            )
            for applicant in applicants
        ]
        
        return ApplicantListResponse(
            applicants=applicant_responses,
            total=len(applicant_responses)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving applicants: {str(e)}"
        )

@router.post("", response_model=ApplicantResponse)
async def create_applicant(
    request: Request,
    applicant_in: ApplicantCreate
) -> ApplicantResponse:
    """
    Create a new applicant.
    """
    try:
        # Create new applicant
        applicant = Applicant(
            id=str(uuid4()),
            fullName=applicant_in.fullName,
            dateOfBirth=applicant_in.dateOfBirth,
            Address=applicant_in.Address,
            contactNumber=applicant_in.contactNumber
        )
        
        # Save to database
        await applicant.insert()
        
        return ApplicantResponse(
            id=str(applicant.id),
            fullName=applicant.fullName,
            dateOfBirth=applicant.dateOfBirth,
            Address=applicant.Address,
            contactNumber=applicant.contactNumber
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating applicant: {str(e)}"
        )