"""Log-only entry processor."""

from typing import Literal

from logzero import logger
from pydantic.dataclasses import dataclass

from feedly_saved_entries_processor.entry_processors.base_entry_processor import (
    BaseEntryProcessor,
)
from feedly_saved_entries_processor.feedly_client import Entry


@dataclass(frozen=True)
class LogOnlyEntryProcessor(BaseEntryProcessor):
    """A processor that only logs the Feedly entry."""

    level: Literal["info", "debug", "warning", "error"] = "info"

    def process_entry(self, entry: Entry) -> None:
        """Process a Feedly entry by logging its details."""
        log_message = f"Processing entry: {entry.title} (URL: {entry.canonical_url})"
        if self.level == "info":
            logger.info(log_message)
        elif self.level == "debug":
            logger.debug(log_message)
        elif self.level == "warning":
            logger.warning(log_message)
        elif self.level == "error":
            logger.error(log_message)
        else:
            logger.info(log_message)  # Default to info
