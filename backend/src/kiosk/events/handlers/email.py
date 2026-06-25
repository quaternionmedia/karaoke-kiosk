"""Email handler.

Ships as a logging stub. When ``settings.email_enabled`` is true the real send
(stdlib ``smtplib``) goes where the TODO comment is.
"""

from __future__ import annotations

import logging

from kiosk.config import Settings
from kiosk.events.signals import EmailSend

logger = logging.getLogger("kiosk.events.email")


class EmailHandler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def on_email_send(self, payload: EmailSend) -> None:
        if not self.settings.email_enabled:
            logger.info(
                "[email:stub] would send to %s subject=%r", payload.to, payload.subject
            )
            return
        # TODO(email): build a MIMEText message and send via smtplib using the
        # smtp_* settings (host/port/user/password/from).
        logger.info("[email] sending to %s subject=%r", payload.to, payload.subject)
