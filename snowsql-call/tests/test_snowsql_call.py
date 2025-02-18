import os
import tempfile
import pytest
import sys
from unittest.mock import patch, MagicMock

# If your script is named your_script.py:
from src.snowsql_call import parse_config_file, main

def test_parse_config_file():
    """
    Test parse_config_file to ensure it correctly
    reads key-value pairs from a file.
    """
    # Create a temporary file with some test content
    content = """snowflakeRole = MY_ROLE
snowflakeWarehouse= MY_WAREHOUSE
key_with_spaces = value with spaces
"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
        file_path = tf.name
        tf.write(content)

    try:
        # Now parse that file
        result = parse_config_file(file_path)
        
        # Check whether the dictionary has the expected contents
        assert result["snowflakeRole"] == "MY_ROLE"
        assert result["snowflakeWarehouse"] == "MY_WAREHOUSE"
        assert result["key_with_spaces"] == "value with spaces"
    finally:
        os.remove(file_path)


@patch("snowflake.connector.connect")
@patch("argparse.ArgumentParser.parse_args")
def test_main_success(mock_parse_args, mock_connect):
    """
    Test that main() successfully connects to Snowflake
    when all required params are provided.
    """

    # 1. Set up mock arguments as if they were provided via CLI
    mock_parse_args.return_value = MagicMock(
        config_file="fake_config.txt",
        secret_file="fake_secret.txt"
    )
    
    # 2. Create temporary config and secret files
    config_content = """snowflakeRole = TEST_ROLE
snowflakeWarehouse = TEST_WAREHOUSE
snowflakeDatabase = TEST_DB
snowflakeSchema = TEST_SCHEMA
"""
    secret_content = """snowflakeAccount = TEST_ACCOUNT
snowflakeUsername = TEST_USER
snowflakePassword = TEST_PASS
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as conf:
        config_path = conf.name
        conf.write(config_content)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as sec:
        secret_path = sec.name
        sec.write(secret_content)

    # 3. We patch parse_args to return those file paths
    mock_parse_args.return_value.config_file = config_path
    mock_parse_args.return_value.secret_file = secret_path
    
    try:
        # 4. Call main()
        #    If everything is correct, it should attempt to connect, 
        #    and print success without calling sys.exit(1).
        #    We rely on the mock_connect to not raise exceptions.
        main()
        
        # Check if connect was called with expected kwargs
        mock_connect.assert_called_once_with(
            account="TEST_ACCOUNT",
            user="TEST_USER",
            password="TEST_PASS",
            role="TEST_ROLE",
            warehouse="TEST_WAREHOUSE",
            database="TEST_DB",
            schema="TEST_SCHEMA"
        )
    finally:
        # Clean up temp files
        os.remove(config_path)
        os.remove(secret_path)


@patch("snowflake.connector.connect")
@patch("argparse.ArgumentParser.parse_args")
@patch("sys.exit")
def test_main_missing_config(mock_sys_exit, mock_parse_args, mock_connect):
    """
    Test that main() calls sys.exit if any required config is missing.
    """

    # Provide a config file missing 'snowflakeRole'
    config_content = """snowflakeWarehouse = TEST_WAREHOUSE
"""
    secret_content = """snowflakeAccount = TEST_ACCOUNT
snowflakeUsername = TEST_USER
snowflakePassword = TEST_PASS
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as conf:
        config_path = conf.name
        conf.write(config_content)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as sec:
        secret_path = sec.name
        sec.write(secret_content)

    mock_parse_args.return_value.config_file = config_path
    mock_parse_args.return_value.secret_file = secret_path

    try:
        # We expect main to call sys.exit due to the missing role
        main()
    finally:
        os.remove(config_path)
        os.remove(secret_path)

    # Check that sys.exit was called (meaning an error was raised)
    mock_sys_exit.assert_called_once()
    # You could also verify the connector didn't even get called
    mock_connect.assert_not_called()


@patch("snowflake.connector.connect", side_effect=Exception("Connection failed"))
@patch("argparse.ArgumentParser.parse_args")
@patch("sys.exit")
def test_main_connection_failure(mock_sys_exit, mock_parse_args, mock_connect):
    """
    Test that main() calls sys.exit(1) if connection to Snowflake fails.
    """

    # Provide valid config values
    config_content = """snowflakeRole = TEST_ROLE
snowflakeWarehouse = TEST_WAREHOUSE
snowflakeDatabase = TEST_DB
snowflakeSchema = TEST_SCHEMA
"""
    secret_content = """snowflakeAccount = TEST_ACCOUNT
snowflakeUsername = TEST_USER
snowflakePassword = TEST_PASS
"""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as conf:
        config_path = conf.name
        conf.write(config_content)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as sec:
        secret_path = sec.name
        sec.write(secret_content)

    mock_parse_args.return_value.config_file = config_path
    mock_parse_args.return_value.secret_file = secret_path

    try:
        main()
    finally:
        os.remove(config_path)
        os.remove(secret_path)

    # We expect sys.exit(1) due to the mocked connection failure
    mock_sys_exit.assert_called_with(1)
    mock_connect.assert_called_once()
