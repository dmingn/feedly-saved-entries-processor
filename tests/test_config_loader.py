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
def test_configs_path() -> Path:
    """Provide the base path to the test configuration files directory."""
    return Path(__file__).parent / "test_configs"


@pytest.fixture
def valid_config_file(test_configs_path: Path) -> Path:
    """Provide a path to a valid configuration file."""
    return test_configs_path / "valid_config.yaml"


@pytest.fixture
def invalid_yaml_file(test_configs_path: Path) -> Path:
    """Provide a path to an invalid YAML file."""
    return test_configs_path / "invalid_yaml.yaml"


@pytest.fixture
def invalid_schema_file(test_configs_path: Path) -> Path:
    """Provide a path to a YAML file with invalid schema."""
    return test_configs_path / "invalid_schema.yaml"


@pytest.mark.usefixtures("mock_todoist_api_token_env")
def test_load_config_success(valid_config_file: Path) -> None:
    """Test that a valid configuration file can be loaded successfully."""
    config = load_config(valid_config_file)

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


def test_load_config_invalid_schema(invalid_schema_file: Path) -> None:
    """Test that ValueError is raised for a YAML file with invalid schema."""
    with pytest.raises(ValueError, match="Error parsing configuration file"):
        load_config(invalid_schema_file)


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
