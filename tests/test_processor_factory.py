"""Tests for the processor_factory module."""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from pytest_mock.plugin import MockerFixture

from feedly_saved_entries_processor.entry_processors.log_only_entry_processor import (
    LogOnlyEntryProcessor,
)
from feedly_saved_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)
from feedly_saved_entries_processor.processor_factory import (
    get_processor,
)


@pytest.fixture
def mock_todoist_api(mocker: MockerFixture) -> MagicMock:
    """Mock TodoistAPI to prevent actual API calls."""
    return mocker.patch(
        "feedly_saved_entries_processor.entry_processors.todoist_entry_processor.TodoistAPI"
    )


@pytest.fixture(autouse=True)
def mock_os_environ_get(mocker: MockerFixture) -> MagicMock:
    """Mock os.environ.get for TODOIST_API_TOKEN."""
    return mocker.patch("os.environ.get", return_value="dummy_token")


def test_get_processor_log_only_success() -> None:
    """Test successful loading of LogOnlyEntryProcessor."""
    config = {"level": "debug"}
    processor = get_processor("log_only", config)

    assert isinstance(processor, LogOnlyEntryProcessor)
    assert processor.level == "debug"


def test_get_processor_todoist_success(mock_todoist_api: MagicMock) -> None:
    """Test successful loading of TodoistEntryProcessor."""
    config = {"project_id": "12345", "priority": 3}
    processor = get_processor("todoist", config)

    assert isinstance(processor, TodoistEntryProcessor)
    assert processor.project_id == "12345"
    assert processor.priority == 3
    mock_todoist_api.assert_called_once_with("dummy_token")


def test_get_processor_unknown_name() -> None:
    """Test that ValueError is raised for an unknown processor name."""
    with pytest.raises(ValueError, match="Unknown processor: unknown_processor"):
        get_processor("unknown_processor", {})


def test_get_processor_log_only_invalid_config() -> None:
    """Test that ValidationError is raised for invalid config for LogOnlyEntryProcessor."""
    # 'level' must be one of the Literal values
    config = {"level": "invalid_level"}
    with pytest.raises(ValidationError):
        get_processor("log_only", config)


def test_get_processor_todoist_invalid_config() -> None:
    """Test that ValidationError is raised for invalid config for TodoistEntryProcessor."""
    # 'project_id' is required
    config = {"priority": 2}
    with pytest.raises(ValidationError):
        get_processor("todoist", config)
