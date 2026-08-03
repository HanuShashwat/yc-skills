import pytest
import sqlite3
import argparse
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import logging

from src.cli import quota_cmd

@pytest.fixture
def memory_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    # Create usage_log table
    cursor.execute("""
    CREATE TABLE usage_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        provider TEXT,
        model TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        success INTEGER,
        latency_ms REAL,
        cost_usd REAL
    )
    """)
    conn.commit()
    yield conn
    conn.close()

def test_quota_cmd_empty(memory_db, caplog, monkeypatch):
    """Test quota_cmd when usage_log is empty (first run)."""
    caplog.set_level(logging.INFO)
    
    # Mock sqlite3.connect to return our memory_db
    monkeypatch.setattr(sqlite3, "connect", lambda db: memory_db)
    
    # Mock db_path.exists() to return True
    monkeypatch.setattr(Path, "exists", lambda self: True)
    
    args = argparse.Namespace()
    
    quota_cmd(args)
    
    # Check that output has 0 usage and OK status
    assert "✓ OK" in caplog.text
    assert "✗ EXHAUSTED" not in caplog.text
    assert "⚠ LOW" not in caplog.text

def test_quota_cmd_seeded(memory_db, caplog, monkeypatch):
    """Test quota_cmd with seeded usage_log data."""
    caplog.set_level(logging.INFO)
    monkeypatch.setattr(sqlite3, "connect", lambda db: memory_db)
    monkeypatch.setattr(Path, "exists", lambda self: True)
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Seed data
    cursor = memory_db.cursor()
    
    # Deepseek: used 45,000 tokens (limit is 500,000)
    cursor.execute("INSERT INTO usage_log (timestamp, provider, total_tokens, success) VALUES (?, ?, ?, ?)",
                   (f"{today}T10:00:00Z", "deepseek", 45000, 1))
                   
    # Kimi: 0 used
    
    # GLM: used 480,000 tokens (limit 500,000) -> 18,000 remaining, LOW status
    cursor.execute("INSERT INTO usage_log (timestamp, provider, total_tokens, success) VALUES (?, ?, ?, ?)",
                   (f"{today}T11:00:00Z", "glm", 480000, 1))
                   
    # Gemini: used 1,500,000 tokens (limit 1,500,000) -> EXHAUSTED
    cursor.execute("INSERT INTO usage_log (timestamp, provider, total_tokens, success) VALUES (?, ?, ?, ?)",
                   (f"{today}T12:00:00Z", "gemini", 1500000, 1))
                   
    memory_db.commit()
    
    args = argparse.Namespace()
    quota_cmd(args)
    
    output = caplog.text
    
    # Check computations
    # Deepseek
    assert "deepseek    | 45,000       | 1,000,000    | 859,500" in output or "859,500" in output
    # Kimi
    assert "kimi" in output
    assert "450,000" in output
    # GLM
    assert "18,000" in output
    assert "⚠ LOW" in output
    # Gemini
    assert "✗ EXHAUSTED" in output
