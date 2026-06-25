"""OBS scene/recording handler.

This ships as a logging stub. When ``settings.obs_enabled`` is true the methods
log the intended OBS actions; the real obs-websocket calls (e.g. via the
``obsws-python`` package) go where the TODO comments are.
"""

from __future__ import annotations

import logging

from kiosk.config import Settings
from kiosk.events.signals import PerformanceFinished, PerformanceStarted

logger = logging.getLogger("kiosk.events.obs")

# Scene names defined in static/Rock_Video.json.
KARAOKE_SCENE = "Karaoke"
BREAK_SCENE = "Break"


class ObsHandler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def on_performance_started(self, payload: PerformanceStarted) -> None:
        if not self.settings.obs_enabled:
            logger.info(
                "[obs:stub] would switch to %s scene and StartRecord "
                "(performance=%s)",
                KARAOKE_SCENE,
                payload.performance_id,
            )
            return
        # TODO(obs): connect via obsws-python, SetCurrentProgramScene(KARAOKE_SCENE),
        # then StartRecord().
        logger.info("[obs] StartRecord + scene=%s", KARAOKE_SCENE)

    def on_performance_finished(self, payload: PerformanceFinished) -> None:
        if not self.settings.obs_enabled:
            logger.info(
                "[obs:stub] would StopRecord and switch to %s scene "
                "(performance=%s)",
                BREAK_SCENE,
                payload.performance_id,
            )
            return
        # TODO(obs): StopRecord() -> capture output path, SetCurrentProgramScene(
        # BREAK_SCENE), then persist the recording file_path/url.
        logger.info("[obs] StopRecord + scene=%s", BREAK_SCENE)
