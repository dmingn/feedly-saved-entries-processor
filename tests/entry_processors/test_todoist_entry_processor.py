"""Tests for the TodoistEntryProcessor."""

import datetime
from collections.abc import Callable
from typing import Literal
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from feedly_saved_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)
from feedly_saved_entries_processor.feedly_client import Entry, Origin, Summary


@pytest.fixture
def mock_todoist_api(mocker: MockerFixture) -> MagicMock:
    """Fixture for mocking TodoistAPI."""
    mock_api: MagicMock = mocker.patch(
        "feedly_saved_entries_processor.entry_processors.todoist_entry_processor.TodoistAPI"
    )
    return mock_api


@pytest.fixture
def todoist_processor(mocker: MockerFixture) -> TodoistEntryProcessor:
    """Fixture for TodoistEntryProcessor instance."""
    mocker.patch.dict("os.environ", {"TODOIST_API_TOKEN": "test_token"})
    project_id = "test_project_id"
    return TodoistEntryProcessor(project_id=project_id)


@pytest.fixture
def entry_builder() -> Callable[..., Entry]:
    """Fixture for a builder function to create Entry objects."""

    def _builder(
        title: str = "Test Entry",
        canonical_url: str | None = "http://example.com/test",
        summary_content: str | None = "Test Summary Content",
    ) -> Entry:
        return Entry(
            id="test_id",
            title=title,
            canonical_url=canonical_url,
            origin=Origin(
                title="Test Origin",
                html_url="http://example.com",
                stream_id="test_stream_id",
            ),
            summary=Summary(content=summary_content) if summary_content else None,
            published=1234567890,
            author=None,
        )

    return _builder


@pytest.fixture
def sample_entry(entry_builder: Callable[..., Entry]) -> Entry:
    """Fixture for a sample Entry object using the builder."""
    return entry_builder()


def test_post_init(
    mock_todoist_api: MagicMock, todoist_processor: TodoistEntryProcessor
) -> None:
    """Test that the Todoist API client is initialized correctly."""
    assert todoist_processor.todoist_client is not None
    assert todoist_processor.todoist_client == mock_todoist_api.return_value


def test_process_entry_success(
    mock_todoist_api: MagicMock,
    todoist_processor: TodoistEntryProcessor,
    entry_builder: Callable[..., Entry],
) -> None:
    """Test successful processing of an entry."""
    sample_entry = entry_builder()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_123"
    mock_instance.add_task.return_value.content = "Test Task"

    todoist_processor.process_entry(sample_entry)

    expected_content = "Test Entry - http://example.com/test"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=todoist_processor.project_id,
        priority=None,
        due_datetime=None,
        description="Test Summary Content",
    )


def test_process_entry_no_canonical_url(
    mock_todoist_api: MagicMock,
    todoist_processor: TodoistEntryProcessor,
    entry_builder: Callable[..., Entry],
) -> None:
    """Test processing of an entry without a canonical URL."""
    entry = entry_builder(
        canonical_url=None, title="Test Entry No URL", summary_content=None
    )
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_456"
    mock_instance.add_task.return_value.content = "Test Task No URL"

    todoist_processor.process_entry(entry)

    expected_content = "Test Entry No URL - http://example.com"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=todoist_processor.project_id,
        priority=None,
        due_datetime=None,
        description=None,
    )


def test_process_entry_add_task_failure(
    mock_todoist_api: MagicMock,
    todoist_processor: TodoistEntryProcessor,
    entry_builder: Callable[..., Entry],
) -> None:
    """Test error handling when adding a task fails."""
    sample_entry = entry_builder()
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        todoist_processor.process_entry(sample_entry)

    mock_instance.add_task.assert_called_once()


def test_process_entry_with_optional_params(
    mock_todoist_api: MagicMock,
    todoist_processor: TodoistEntryProcessor,
    entry_builder: Callable[..., Entry],
) -> None:
    """Test processing of an entry with optional parameters (due_datetime, priority)."""
    due_datetime = datetime.datetime(2025, 12, 31, 23, 59, 59, tzinfo=datetime.UTC)
    priority: Literal[1, 2, 3, 4] = 2  # Use Literal for type hint

    todoist_processor.due_datetime = due_datetime
    todoist_processor.priority = priority

    entry = entry_builder(
        title="Entry with Params",
        canonical_url="http://example.com/params",
        summary_content="Summary for params",
    )
    mock_instance = mock_todoist_api.return_value
    mock_instance.add_task.return_value.id = "task_789"
    mock_instance.add_task.return_value.content = "Test Task with Params"

    todoist_processor.process_entry(entry)

    expected_content = "Entry with Params - http://example.com/params"
    mock_instance.add_task.assert_called_once_with(
        content=expected_content,
        project_id=todoist_processor.project_id,
        priority=priority,
        due_datetime=due_datetime,
        description="Summary for params",
    )
