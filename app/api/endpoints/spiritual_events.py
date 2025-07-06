from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from starlette.authentication import requires
from app.utils.s3 import upload_file, delete_file, get_presigned_url

from app.core.models.SpiritualEvent import SpiritualEvent
from app.core.schemas.SpiritualEvent import (
    SpiritualEventBase, SpiritualEventCreate, SpiritualEventUpdate,
    SpiritualEventResponse, SpiritualEventListResponse
)

router = APIRouter()

@router.post("", response_model=SpiritualEventResponse)
@requires("authenticated")
async def createSpiritualEvent(
    request: Request,
    eventTitle: str = Form(...),
    shortDescription: str = Form(...),
    longDescription: str = Form(...),
    eventDate: datetime = Form(...),
    mainImage: UploadFile = File(...),
    additionalImages: List[UploadFile] = File(None),
    videos: List[str] = Form(None)
) -> SpiritualEventResponse:
    # Upload main image
    mainImageKey = "spiritual_events"
    mainImageKey = await upload_file(mainImage, mainImageKey)

    # Upload additional images
    additionalImageKeys = []
    if additionalImages:
        for image in additionalImages:
            imageKey = "spiritual_events/images"
            imageKey = await upload_file(image, imageKey)
            additionalImageKeys.append(imageKey)

    # Create event
    event = await SpiritualEvent(
        id=str(uuid4()),
        eventTitle=eventTitle,
        shortDescription=shortDescription,
        longDescription=longDescription,
        eventDate=eventDate,
        mainImage=mainImageKey,
        additionalImages=additionalImageKeys,
        videos=videos,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    ).save()

    # Add presigned URLs for response
    response_event = event.dict()
    response_event["mainImage"] = get_presigned_url(mainImageKey)
    response_event["additionalImages"] = [get_presigned_url(key) for key in additionalImageKeys]
    
    return response_event

@router.get("", response_model=SpiritualEventListResponse)
async def getSpiritualEvents(
    skip: int = 0,
    limit: int = 10
) -> SpiritualEventListResponse:
    total = await SpiritualEvent.find().count()
    events = await SpiritualEvent.find().to_list()
    
    # Add presigned URLs for response
    response_events = []
    for event in events:
        event_dict = event.dict()
        event_dict["mainImage"] = get_presigned_url(event.mainImage)
        event_dict["additionalImages"] = [get_presigned_url(key) for key in event.additionalImages]
        response_events.append(event_dict)
    
    return SpiritualEventListResponse(total=total, items=response_events)

@router.get("/{event_id}", response_model=SpiritualEventResponse)
async def getSpiritualEvent(event_id: str) -> SpiritualEventResponse:
    event = await SpiritualEvent.find_one(SpiritualEvent.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spiritual Event with ID {event_id} not found"
        )
    
    # Add presigned URLs for response
    response_event = event.dict()
    response_event["mainImage"] = get_presigned_url(event.mainImage)
    response_event["additionalImages"] = [get_presigned_url(key) for key in event.additionalImages]
    
    return response_event

@router.put("/{event_id}", response_model=SpiritualEventResponse)
@requires("authenticated")
async def updateSpiritualEvent(
    request: Request,
    event_id: str,
    eventTitle: Optional[str] = Form(None),
    shortDescription: Optional[str] = Form(None),
    longDescription: Optional[str] = Form(None),
    eventDate: Optional[datetime] = Form(None),
    mainImage: Optional[UploadFile] = File(None),
    additionalImages: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[str]] = Form(None)
) -> SpiritualEventResponse:
    event = await SpiritualEvent.find_one(SpiritualEvent.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spiritual Event with ID {event_id} not found"
        )

    update_data = {}
    if eventTitle is not None:
        update_data["eventTitle"] = eventTitle
    if shortDescription is not None:
        update_data["shortDescription"] = shortDescription
    if longDescription is not None:
        update_data["longDescription"] = longDescription
    if eventDate is not None:
        update_data["eventDate"] = eventDate
    if videos is not None:
        update_data["videos"] = videos

    # Handle main image update
    if mainImage:
        # Delete old image
        await delete_file(event.mainImage)
        
        # Upload new image
        mainImageKey = "spiritual_events"
        mainImageKey = await upload_file(mainImage, mainImageKey)
        update_data["mainImage"] = mainImageKey

    # Handle additional images update
    if additionalImages:
        # Delete old images
        for key in event.additionalImages:
            await delete_file(key)
        
        # Upload new images
        additionalImageKeys = []
        for image in additionalImages:
            imageKey = "spiritual_events/images"
            imageKey = await upload_file(image, imageKey)
            additionalImageKeys.append(imageKey)
        update_data["additionalImages"] = additionalImageKeys

    update_data["updatedAt"] = datetime.utcnow()
    await event.update({"$set": update_data})
    
    # Get updated event
    updated_event = await SpiritualEvent.find_one(SpiritualEvent.id == event_id)
    
    # Add presigned URLs for response
    response_event = updated_event.dict()
    response_event["mainImage"] = get_presigned_url(updated_event.mainImage)
    response_event["additionalImages"] = [get_presigned_url(key) for key in updated_event.additionalImages]
    response_event["videos"] = [get_presigned_url(key) for key in updated_event.videos]
    
    return response_event

@router.delete("/{event_id}")
@requires("authenticated")
async def deleteSpiritualEvent(
    request: Request,
    event_id: str
) -> dict:
    event = await SpiritualEvent.find_one(SpiritualEvent.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spiritual Event with ID {event_id} not found"
        )

    # Delete main image
    delete_file(event.mainImage)

    # Delete additional images
    for key in event.additionalImages:
        delete_file(key)

    await event.delete()
    return {"message": "Spiritual Event deleted successfully"}
