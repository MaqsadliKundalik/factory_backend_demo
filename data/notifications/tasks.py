import logging
from celery import shared_task
from firebase_admin import messaging

from apps.common.firebase import get_firebase_app
from data.notifications.models import Notification
from data.session.models import DriverSession, FactoryUserSession

BATCH_SIZE = 500
logger = logging.getLogger(__name__)


def _get_sessions(to_role, to_user_id=None):
    if to_role == "driver":
        qs = DriverSession.objects.filter(fcm_invalid=False)
        if to_user_id:
            qs = qs.filter(driver_id=to_user_id)
    else:
        qs = FactoryUserSession.objects.filter(
            factory_user__role=to_role, fcm_invalid=False
        )
        if to_user_id:
            qs = qs.filter(factory_user_id=to_user_id)
    return list(qs.exclude(fcm_token__isnull=True).exclude(fcm_token=""))


def _send_batch(sessions, notification):
    tokens = [s.fcm_token for s in sessions]
    msg = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(
            title=notification.title,
            body=notification.message,
        ),
        data={"notification_id": str(notification.id)},
    )
    logger.info(
        "Sending Firebase multicast for notification_id=%s to %s tokens",
        notification.id,
        len(tokens),
    )
    batch_response = messaging.send_each_for_multicast(msg)

    invalid_ids = []
    for i, resp in enumerate(batch_response.responses):
        if not resp.success:
            text = str(resp.exception)
            logger.warning(
                "Firebase send failed for notification_id=%s session_id=%s error=%s",
                notification.id,
                sessions[i].pk,
                text,
            )
            if (
                "registration-token-not-registered" in text
                or "UNREGISTERED" in text.upper()
            ):
                invalid_ids.append(sessions[i].pk)

    if invalid_ids:
        # bulk update - bitta query
        type(sessions[0]).objects.filter(pk__in=invalid_ids).update(fcm_invalid=True)

    return batch_response.success_count, batch_response.failure_count


@shared_task
def send_notification(notification_id):
    logger.info("send_notification task started for notification_id=%s", notification_id)
    notification = Notification.objects.filter(id=notification_id).first()
    if not notification:
        logger.warning("Notification not found for notification_id=%s", notification_id)
        return "Notification not found"

    if not get_firebase_app():
        logger.warning(
            "Firebase is not configured or initialization failed for notification_id=%s",
            notification_id,
        )
        return "Firebase not configured, push skipped"

    sessions = _get_sessions(notification.to_role, notification.to_user_id)
    logger.info(
        "Notification_id=%s resolved %s sessions for to_role=%s to_user_id=%s",
        notification_id,
        len(sessions),
        notification.to_role,
        notification.to_user_id,
    )
    if not sessions:
        return {"total": 0, "sent": 0, "failed": 0}

    total = len(sessions)
    sent = failed = 0

    for i in range(0, total, BATCH_SIZE):
        batch_sent, batch_failed = _send_batch(
            sessions[i : i + BATCH_SIZE], notification
        )
        sent += batch_sent
        failed += batch_failed

    return {"total": total, "sent": sent, "failed": failed}
