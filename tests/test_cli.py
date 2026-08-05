"""
Tests for OpenYC Skills CLI.
"""
import pytest
import subprocess
import sys
from pathlib import Path

COMMANDS = [
    "init-db",
    "ingest-library",
    "ingest-youtube",
    "chunk",
    "forge",
    "link",
    "validate",
    "export",
    "index",
    "reaper",
    "quota",
    "backfill"
]

def run_cli(*args):
    """Helper to run the CLI."""
    cmd = [sys.executable, "-m", "src.cli"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

def test_cli_help():
    """Verify python -m src.cli --help exits with code 0 and contains all 12 command names."""
    res = run_cli("--help")
    assert res.returncode == 0
    assert "OpenYC Skills — Static skill file generator for AI agents." in res.stdout
    for cmd in COMMANDS:
        assert cmd in res.stdout

@pytest.mark.parametrize("command", COMMANDS)
def test_command_help(command):
    """Verify each command's --help exits with code 0."""
    res = run_cli(command, "--help")
    assert res.returncode == 0

def test_init_db(tmp_path, monkeypatch):
    """Test init-db creates the database."""
    db_file = tmp_path / "test.db"
    
    import src.cli
    monkeypatch.setattr(src.cli, "DB_PATH", str(db_file))
    
    from src.cli import main
    monkeypatch.setattr(sys, "argv", ["src.cli", "init-db"])
    
    main()
    
    assert db_file.exists()

def test_missing_db_errors(tmp_path, monkeypatch, caplog):
    """Commands that require the database print a clear error if DB doesn't exist."""
    db_file = tmp_path / "nonexistent.db"
    
    import src.cli
    import logging
    caplog.set_level(logging.ERROR)
    
    monkeypatch.setattr(src.cli, "DB_PATH", str(db_file))
    from src.cli import main
    
    # test reaper
    monkeypatch.setattr(sys, "argv", ["src.cli", "reaper"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    assert "Database not found." in caplog.text
    
    caplog.clear()
    
    # test quota
    monkeypatch.setattr(sys, "argv", ["src.cli", "quota"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    assert "Database not found." in caplog.text

def test_invalid_arguments():
    """Invalid arguments produce clear error messages."""
    res = run_cli("forge", "--batch-size", "abc")
    assert res.returncode != 0
    assert "invalid int value: 'abc'" in res.stderr
