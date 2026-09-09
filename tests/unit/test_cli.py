"""Tests for the Mycelium CLI."""

import sys
import pytest
from unittest.mock import patch, MagicMock
from micelio.cli import main

@patch("sys.argv", ["mycelium-cli", "--key", "test-key", "health"])
@patch("httpx.Client.get")
def test_cli_health(mock_get, capsys):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "ok"}
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp
    
    main()
    
    captured = capsys.readouterr()
    assert "OK -" in captured.out
    assert "ok" in captured.out
    mock_get.assert_called_once_with("/health")

@patch("sys.argv", ["mycelium-cli", "--key", "test-key", "tenant-create", "--id", "t1", "--name", "Test"])
@patch("httpx.Client.post")
def test_cli_tenant_create(mock_post, capsys):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"tenant_id": "t1"}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp
    
    main()
    
    captured = capsys.readouterr()
    assert "Tenant created successfully" in captured.out
    mock_post.assert_called_once()
