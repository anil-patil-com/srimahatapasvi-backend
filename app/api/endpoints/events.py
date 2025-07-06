from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Request
from starlette.authentication import requires
from app.utils.s3 import upload_file, delete_file, get_presigned_url

from app.core.models.Event import Event
from app.core.schemas.Event import (
    EventType, EventBase, EventCreateRequest, EventUpdateRequest,
    EventResponse, EventListResponse
)

router = APIRouter()

@router.post("", response_model=EventResponse)
@requires("authenticated")
async def createEvent(
    request: Request,
    eventTitle: str = Form(...),
    shortDescription: str = Form(...),
    longDescription: str = Form(...),
    eventType: EventType = Form(...),
    eventDate: datetime = Form(...),
    mainImage: UploadFile = File(...),
    additionalImages: List[UploadFile] = File(None),
    videos: List[str] = Form(None)
) -> EventResponse:
    # Upload main image
    mainImageKey = f"events/{eventType.value}/{eventTitle}"
    mainImageKey = await upload_file(mainImage, mainImageKey)

    # Upload additional images
    additionalImageKeys = []
    if additionalImages:
        for image in additionalImages:
            imageKey = f"events/{eventType.value}/{eventTitle}/images"
            imageKey = await upload_file(image, imageKey)
            additionalImageKeys.append(imageKey)

    # Create event
    event = await Event(
        id=str(uuid4()),
        eventTitle=eventTitle,
        shortDescription=shortDescription,
        longDescription=longDescription,
        eventType=eventType,
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

@router.get("", response_model=EventListResponse)
async def getEvents(
    eventType: Optional[EventType] = None
) -> EventListResponse:
    query = {}
    if eventType:
        query["eventType"] = eventType

    total = await Event.find(query).count()
    events = await Event.find(query).to_list()
    
    # Add presigned URLs for response
    response_events = []
    for event in events:
        event_dict = event.dict()
        event_dict["mainImage"] = get_presigned_url(event.mainImage)
        event_dict["additionalImages"] = [get_presigned_url(key) for key in event.additionalImages]
        response_events.append(event_dict)
    
    return EventListResponse(total=total, items=response_events)

@router.get("/{event_id}", response_model=EventResponse)
async def getEvent(event_id: str) -> EventResponse:
    event = await Event.find_one(Event.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    # Add presigned URLs for response
    response_event = event.dict()
    response_event["mainImage"] = get_presigned_url(event.mainImage)
    response_event["additionalImages"] = [get_presigned_url(key) for key in event.additionalImages]
    
    return response_event

@router.put("/{event_id}", response_model=EventResponse)
@requires("authenticated")
async def updateEvent(
    request: Request,
    event_id: str,
    eventTitle: Optional[str] = Form(None),
    shortDescription: Optional[str] = Form(None),
    longDescription: Optional[str] = Form(None),
    eventType: Optional[EventType] = Form(None),
    eventDate: Optional[datetime] = Form(None),
    mainImage: UploadFile = File(None),
    additionalImages: List[UploadFile] = File(None),
    videos: List[str] = Form(None)
) -> EventResponse:
    event = await Event.find_one(Event.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    update_data = {}
    if eventTitle is not None:
        update_data["eventTitle"] = eventTitle
    if shortDescription is not None:
        update_data["shortDescription"] = shortDescription
    if longDescription is not None:
        update_data["longDescription"] = longDescription
    if eventType is not None:
        update_data["eventType"] = eventType
    if eventDate is not None:
        update_data["eventDate"] = eventDate
    if videos is not None:
        update_data['videos'] = videos
    eventTitle = event.eventTitle
    # Handle main image update
    if mainImage:
        # Delete old image
        delete_file(event.mainImage)
        
        # Upload new image
        mainImageKey = f"events/{event.eventType.value}/{eventTitle}"
        mainImageKey = await upload_file(mainImage, mainImageKey)
        update_data["mainImage"] = mainImageKey

    # Handle additional images update
    if additionalImages:
        # Delete old images
        for key in event.additionalImages:
            delete_file(key)
        
        # Upload new images
        additionalImageKeys = []
        for image in additionalImages:
            imageKey = f"events/{event.eventType.value}/{eventTitle}/images"
            imageKey = await upload_file(image, imageKey)
            additionalImageKeys.append(imageKey)
        update_data["additionalImages"] = additionalImageKeys

    update_data["updatedAt"] = datetime.utcnow()
    await event.update({"$set": update_data})
    
    # Get updated event
    updated_event = await Event.find_one(Event.id == event_id)
    
    # Add presigned URLs for response
    response_event = updated_event.dict()
    response_event["mainImage"] = get_presigned_url(updated_event.mainImage)
    response_event["additionalImages"] = [get_presigned_url(key) for key in updated_event.additionalImages]
    
    return response_event

@router.delete("/{event_id}")
@requires("authenticated")
async def deleteEvent(
    request: Request,
    event_id: str
) -> dict:
    event = await Event.find_one(Event.id == event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )

    # Delete main image
    delete_file(event.mainImage)

    # Delete additional images
    for key in event.additionalImages:
        delete_file(key)

    await event.delete()
    return {"message": "Event deleted successfully"}
