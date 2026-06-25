"""Event bus and default handler tests."""

from __future__ import annotations

import logging

from kiosk.config import Settings
from kiosk.events.bus import EventBus
from kiosk.events.handlers import register_default_handlers
from kiosk.events.handlers.obs import BREAK_SCENE, KARAOKE_SCENE, ObsHandler
from kiosk.events.handlers.email import EmailHandler
from kiosk.events.signals import (
    EMAIL_SEND,
    PERFORMANCE_FINISHED,
    PERFORMANCE_STARTED,
    EmailSend,
    PerformanceFinished,
    PerformanceStarted,
)


def test_bus_calls_all_subscribers():
    bus = EventBus()
    calls = []
    bus.subscribe("e", lambda p: calls.append(("a", p)))
    bus.subscribe("e", lambda p: calls.append(("b", p)))
    bus.emit("e", 42)
    assert calls == [("a", 42), ("b", 42)]


def test_raising_handler_is_swallowed():
    bus = EventBus()
    seen = []

    def boom(_):
        raise RuntimeError("nope")

    bus.subscribe("e", boom)
    bus.subscribe("e", lambda p: seen.append(p))
    bus.emit("e", 1)  # must not raise
    assert seen == [1]


def test_obs_handler_logs_scenes(caplog):
    handler = ObsHandler(Settings(obs_enabled=False))
    with caplog.at_level(logging.INFO, logger="kiosk.events.obs"):
        handler.on_performance_started(
            PerformanceStarted(1, "tok", 1, 1, None, None)
        )
        handler.on_performance_finished(PerformanceFinished(1, "tok", None))
    text = caplog.text
    assert KARAOKE_SCENE in text
    assert BREAK_SCENE in text


def test_email_handler_logs_recipient(caplog):
    handler = EmailHandler(Settings(email_enabled=False))
    with caplog.at_level(logging.INFO, logger="kiosk.events.email"):
        handler.on_email_send(EmailSend(to="x@y.com", subject="Hi", body="b"))
    assert "x@y.com" in caplog.text


def test_register_default_handlers_subscribes():
    bus = EventBus()
    register_default_handlers(bus, Settings())
    assert bus.handlers_for(PERFORMANCE_STARTED)
    assert bus.handlers_for(PERFORMANCE_FINISHED)
    assert bus.handlers_for(EMAIL_SEND)
