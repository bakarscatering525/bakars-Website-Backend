from fastapi import APIRouter, HTTPException, status

from app.schemas.contact import ContactMessage, ContactResponse
from app.services.email_service import (
    EmailNotConfiguredError,
    send_contact_email,
)

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a contact message",
)
async def submit_contact_form(payload: ContactMessage) -> ContactResponse:
    """
    Receive a contact form submission and forward it via email.
    """
    try:
        await send_contact_email(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            message=payload.message,
        )
    except EmailNotConfiguredError as config_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(config_error),
        ) from config_error
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send contact message.",
        ) from exc

    return ContactResponse(
        success=True,
        message="Message sent successfully! We will reach out soon.",
    )
