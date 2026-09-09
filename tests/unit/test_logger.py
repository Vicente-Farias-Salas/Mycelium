"""Unit tests for the logger."""

import json
from micelio.core.logger import logger

def test_json_logger_output(caplog):
    logger.info("Test message", extra={"extra_ctx": {"user_id": 123}})
    
    # In pytest, caplog captures the records
    record = caplog.records[0]
    
    # We can format it manually to check the JSON format
    formatter = logger.handlers[0].formatter
    output = formatter.format(record)
    
    parsed = json.loads(output)
    
    assert parsed["message"] == "Test message"
    assert parsed["level"] == "INFO"
    assert parsed["context"]["user_id"] == 123
