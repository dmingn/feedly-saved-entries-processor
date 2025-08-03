"""Base class for processing Feedly entries."""

from abc import ABC, abstractmethod

from feedly_saved_entries_processor.feedly_client import Entry


class BaseEntryProcessor(ABC):
    """Base class for processing Feedly entries."""

    @abstractmethod
    def process_entry(self, entry: Entry) -> None:
        """Process a single Feedly entry."""
