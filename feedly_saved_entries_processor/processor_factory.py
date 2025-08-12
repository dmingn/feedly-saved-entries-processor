"""Factory for dynamically loading entry processors."""

from types import MappingProxyType
from typing import Any

from feedly_saved_entries_processor.entry_processors.base_entry_processor import (
    BaseEntryProcessor,
)
from feedly_saved_entries_processor.entry_processors.log_only_entry_processor import (
    LogOnlyEntryProcessor,
)
from feedly_saved_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)

PROCESSOR_MAPPING: MappingProxyType[str, type[BaseEntryProcessor]] = MappingProxyType(
    {
        "todoist": TodoistEntryProcessor,
        "log_only": LogOnlyEntryProcessor,
        # Add other processors here as they are implemented
    }
)


def get_processor(
    processor_name: str, raw_config: dict[str, Any]
) -> BaseEntryProcessor:
    """Dynamically loads and returns an initialized entry processor.

    Args:
        processor_name: The name of the processor to load (e.g., "todoist").
        raw_config: The raw configuration dictionary for the processor.

    Returns
    -------
        An initialized instance of BaseEntryProcessor.

    Raises
    ------
        ValueError: If the processor name is not recognized or the processor cannot be loaded.
    """
    if processor_name not in PROCESSOR_MAPPING:
        msg = f"Unknown processor: {processor_name}"
        raise ValueError(msg)

    processor_class = PROCESSOR_MAPPING[processor_name]

    try:
        return processor_class(**raw_config)
    except (ImportError, AttributeError) as e:
        msg = f"Could not load processor {processor_name}: {e}"
        raise ValueError(msg) from e
