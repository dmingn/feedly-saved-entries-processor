"""Tests for the config_loader module."""

from pathlib import Path

import pytest

from feedly_saved_entries_processor.config_loader import (
    Config,
    MatchConfig,
    Rule,
    load_config,
    save_config,
)


@pytest.fixture
def temp_config_file(tmp_path: Path) -> Path:
    """Provide a path to a temporary valid configuration file."""
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


def test_load_config_success(temp_config_file: Path) -> None:
    """Test that a valid configuration file can be loaded successfully."""
    config = load_config(temp_config_file)

    assert isinstance(config, Config)
    assert len(config.rules) == 2

    rule1 = config.rules[0]
    assert rule1.name == "Test Rule 1"
    assert rule1.match.stream_id_in == ("feed/test.com/1", "feed/test.com/2")
    assert rule1.processor == "todoist"
    assert rule1.processor_config is not None
    assert rule1.processor_config["project"] == "Inbox"
    assert rule1.processor_config["priority"] == 4

    rule2 = config.rules[1]
    assert rule2.name == "Test Rule 2"
    assert rule2.match.stream_id_in == ("feed/test.com/3",)
    assert rule2.processor == "log_only"
    assert rule2.processor_config is not None
    assert rule2.processor_config["level"] == "info"


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


def test_save_config_and_load_back(tmp_path: Path) -> None:
    """Test that a Config object can be saved and loaded back correctly."""
    original_config = Config(
        rules=[
            Rule(
                name="Saved Rule",
                match=MatchConfig(stream_id_in=["feed/saved.com/1"]),
                processor="test_processor",
                processor_config={"key": "value"},
            )
        ]
    )
    output_file = tmp_path / "saved_config.yaml"

    save_config(original_config, output_file)

    loaded_config = load_config(output_file)

    assert loaded_config == original_config
