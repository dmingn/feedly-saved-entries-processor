"""Tests for the config_loader module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from feedly_saved_entries_processor.config_loader import (
    Config,
    Rule,
    load_config,
    save_config,
)
from feedly_saved_entries_processor.entry_processors.log_entry_processor import (
    LogEntryProcessor,
)
from feedly_saved_entries_processor.entry_processors.todoist_entry_processor import (
    TodoistEntryProcessor,
)
from feedly_saved_entries_processor.rule_matcher import AllMatcher, StreamIdInMatcher


@pytest.fixture
def mock_todoist_api_token_env(mocker: MockerFixture) -> None:
    """Mock the TODOIST_API_TOKEN environment variable."""
    mocker.patch.dict("os.environ", {"TODOIST_API_TOKEN": "dummy_token"})


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Provide a path to a temporary valid configuration file."""
    content = """
rules:
  - name: "Test Rule 1 - Todoist"
    match:
      matcher_name: "stream_id_in"
      stream_ids:
        - "feed/test.com/1"
        - "feed/test.com/2"
    processor:
      processor_name: "todoist"
      project_id: "Inbox"
      priority: 4

  - name: "Test Rule 2 - Log"
    match:
      matcher_name: "stream_id_in"
      stream_ids:
        - "feed/test.com/3"
    processor:
      processor_name: "log"
      level: "info"

  - name: "Test Rule 3 - All Matcher Log"
    match:
      matcher_name: "all"
    processor:
      processor_name: "log"
      level: "debug"
"""
    file_path = tmp_path / "config.yaml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def invalid_yaml_file(tmp_path: Path) -> Path:
    """Provide a path to a temporary invalid YAML file."""
    content = """
rules:
  - name: "Test Rule 1"
    match:
      stream_id_in:
        - "feed/test.com/1"
        - "feed/test.com/2"
    processor: "todoist"
    processor_config:
      project: "Inbox"
      priority: 4

  - name: "Test Rule 2"
    match:
      stream_id_in:
        - "feed/test.com/3"
    processor: "log_only"
    processor_config:
      level: "info"

  - name: "Invalid YAML: missing colon"
    match
      stream_id_in:
        - "feed/test.com/4"
"""
    file_path = tmp_path / "invalid_config.yaml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def invalid_structure_file(tmp_path: Path) -> Path:
    """Provide a path to a temporary YAML file with invalid structure."""
    content = """
rules:
  - name: "Test Rule 1"
    # Missing 'match' key
    processor: "todoist"
    processor_config:
      project: "Inbox"
"""
    file_path = tmp_path / "invalid_structure.yaml"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def invalid_processor_config_file(tmp_path: Path) -> Path:
    """Provide a path to a temporary YAML file with invalid processor configuration."""
    content = """
rules:
  - name: "Invalid Todoist Processor"
    match:
      matcher_name: "all"
    processor:
      processor_name: "todoist"
      # Missing required 'project_id'
      priority: 4

  - name: "Invalid Log Processor"
    match:
      matcher_name: "all"
    processor:
      processor_name: "log"
      level: "invalid_level" # Invalid level
"""
    file_path = tmp_path / "invalid_processor_config.yaml"
    file_path.write_text(content)
    return file_path


@pytest.mark.usefixtures("mock_todoist_api_token_env")
def test_load_config_success(temp_config_file: Path) -> None:
    """Test that a valid configuration file can be loaded successfully."""
    config = load_config(temp_config_file)

    assert isinstance(config, Config)
    assert len(config.rules) == 3

    rule1 = config.rules[0]
    assert rule1.name == "Test Rule 1 - Todoist"
    assert isinstance(rule1.match, StreamIdInMatcher)
    assert rule1.match.stream_ids == ("feed/test.com/1", "feed/test.com/2")
    assert isinstance(rule1.processor, TodoistEntryProcessor)
    assert rule1.processor.processor_name == "todoist"
    assert rule1.processor.project_id == "Inbox"
    assert rule1.processor.priority == 4

    rule2 = config.rules[1]
    assert rule2.name == "Test Rule 2 - Log"
    assert isinstance(rule2.match, StreamIdInMatcher)
    assert rule2.match.stream_ids == ("feed/test.com/3",)
    assert isinstance(rule2.processor, LogEntryProcessor)
    assert rule2.processor.processor_name == "log"
    assert rule2.processor.level == "info"

    rule3 = config.rules[2]
    assert rule3.name == "Test Rule 3 - All Matcher Log"
    assert isinstance(rule3.match, AllMatcher)
    assert rule3.match.matcher_name == "all"
    assert isinstance(rule3.processor, LogEntryProcessor)
    assert rule3.processor.processor_name == "log"
    assert rule3.processor.level == "debug"


def test_load_config_file_not_found(tmp_path: Path) -> None:
    """Test that FileNotFoundError is raised for a non-existent file."""
    non_existent_file = tmp_path / "non_existent.yaml"
    with pytest.raises(FileNotFoundError):
        load_config(non_existent_file)


def test_load_config_invalid_yaml(invalid_yaml_file: Path) -> None:
    """Test that ValueError is raised for an invalid YAML file."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_yaml_file)


def test_load_config_invalid_structure(invalid_structure_file: Path) -> None:
    """Test that ValueError is raised for a YAML file with invalid structure."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_structure_file)


@pytest.mark.usefixtures("mock_todoist_api_token_env")
def test_load_config_invalid_processor_config(
    invalid_processor_config_file: Path,
) -> None:
    """Test that ValidationError is raised for invalid processor configuration in YAML."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_processor_config_file)


@pytest.mark.usefixtures("mock_todoist_api_token_env")
def test_save_config_and_load_back(tmp_path: Path) -> None:
    """Test that a Config object can be saved and loaded back correctly."""
    original_config = Config(
        rules=[
            Rule(
                name="Saved Rule",
                match=StreamIdInMatcher(
                    matcher_name="stream_id_in", stream_ids=("feed/saved.com/1",)
                ),
                processor=LogEntryProcessor(
                    processor_name="log",
                    level="info",
                ),
            )
        ]
    )
    output_file = tmp_path / "saved_config.yaml"

    save_config(original_config, output_file)

    loaded_config = load_config(output_file)

    assert loaded_config == original_config
