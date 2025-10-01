"""Pytest configuration and fixtures."""

import pytest
import os
from unittest.mock import patch, mock_open

# Mock environment variables for all tests
@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables for all tests."""
    with patch.dict(os.environ, {
        'TELEGRAM_TOKEN': 'test_token',
        'ADMIN_IDS': '123456789',
        'IVASMS_EMAIL': 'test@example.com',
        'IVASMS_PASSWORD': 'test_password',
        'POLL_INTERVAL': '8',
        'HEADLESS': 'true',
        'LOG_LEVEL': 'INFO'
    }):
        yield

# Mock config.yaml file for all tests
@pytest.fixture(autouse=True)
def mock_config_file():
    """Mock config.yaml file for all tests."""
    config_content = """
site:
  base_url: "https://www.ivasms.com"
  login_path: "/login"
  sms_path: "/portal/sms/received"

playwright:
  timeout_ms: 30000
  retries: 3
  headless: true

telegram:
  notify_on_start: true
  notify_on_errors: true
  max_message_length: 4096

selectors:
  login:
    email_input: 'input[name="email"]'
    password_input: 'input[name="password"]'
    login_button: 'button[type="submit"]'
  
  popup:
    next_button: 'button:has-text("Next")'
    done_button: 'button:has-text("Done")'
    popup_container: '.popup, .modal, [role="dialog"]'
  
  navigation:
    client_system: 'a[role="menuitem"]:has-text("Client System")'
    sms_statistics: 'a:has-text("My SMS Statistics")'
  
  sms_page:
    message_list: '.message-list, table tbody, .sms-container'
    message_row: 'tr.sms-row, .sms-item, .message-item'
    sender: '.sender, .phone, .from'
    message_body: '.body, .message, .content'
    timestamp: '.time, .date, .timestamp'
  
  history:
    start_date: 'input[name="Start Date"]'
    end_date: 'input[name="End Date"]'
    get_sms_button: 'button:has-text("Get SMS")'
    loading_spinner: '.spinner, .loading, .fa-spinner'

storage:
  type: "sqlite"
  file: "bot_data.db"
  backup_interval: 3600
"""
    
    with patch('builtins.open', mock_open(read_data=config_content)):
        yield
