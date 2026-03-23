from data.session.models import DriverSession, FactoryUserSession


def normalize_fcm_token(value) -> str | None:
    if value is None:
        return None
    token = str(value).strip()
    return token or None


def claim_fcm_token(*, session_id, token: str, role: str) -> None:
    """Ensure the FCM token belongs to only one session."""
    if role == 'driver':
        DriverSession.objects.filter(fcm_token=token).exclude(id=session_id).update(
            fcm_token=None, fcm_invalid=False
        )
    else:
        FactoryUserSession.objects.filter(fcm_token=token).exclude(id=session_id).update(
            fcm_token=None, fcm_invalid=False
        )
