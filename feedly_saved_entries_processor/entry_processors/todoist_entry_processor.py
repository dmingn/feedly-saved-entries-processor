"""Todoist entry processor."""

import datetime
import os
from dataclasses import dataclass, field
from typing import Literal

from logzero import logger
from todoist_api_python.api import TodoistAPI

from feedly_saved_entries_processor.entry_processors.base_entry_processor import (
    BaseEntryProcessor,
)
from feedly_saved_entries_processor.feedly_client import Entry


@dataclass()
class TodoistEntryProcessor(BaseEntryProcessor):
    """A processor that saves Feedly entries as tasks in Todoist."""

    project_id: str
    due_datetime: datetime.datetime | None = None
    priority: Literal[1, 2, 3, 4] | None = None

    todoist_client: TodoistAPI = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the Todoist API client."""
        api_token = os.environ.get("TODOIST_API_TOKEN")
        if not api_token:
            error_message = "TODOIST_API_TOKEN environment variable must be set"
            raise ValueError(error_message)

        self.todoist_client = TodoistAPI(api_token)

    def process_entry(self, entry: Entry) -> None:
        """Process a Feedly entry by adding it as a task to Todoist."""
        task_content = f"{entry.title} - {entry.canonical_url or entry.origin.html_url if entry.origin else 'No URL'}"

        try:
            task = self.todoist_client.add_task(
                content=task_content,
                project_id=self.project_id,
                priority=self.priority,
                due_datetime=self.due_datetime,
                description=entry.summary.content if entry.summary else None,
            )
        except Exception as e:
            logger.error(f"Failed to add task to Todoist: {e}")
            raise

        logger.info(f"Added task to Todoist: {task.content} (ID: {task.id})")
