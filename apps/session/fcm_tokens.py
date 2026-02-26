from __future__ import annotations

from django.utils import timezone

from apps.sessions.models import DriverSession


def normalize_fcm_token(value) -> str | None:
    if value is None:
        return None
    token = str(value).strip()
    return token or None    


def claim_fcm_token_for_driver_session(*, session_id, token: str) -> None:
    now = timezone.now()
    DriverSession.objects.filter(fcm_token=token).exclude(id=session_id).update(
        fcm_token=None,
        invalid_fcm=False,
        updated_at=now,
    )
