"""Uvicorn entrypoint: ``uvicorn kiosk.main:app``."""

import logging

from kiosk.app import create_app

# Surface kiosk INFO logs (including the OBS/email hook stubs) when run directly.
logging.basicConfig(level=logging.INFO)
logging.getLogger("kiosk").setLevel(logging.INFO)

app = create_app()
