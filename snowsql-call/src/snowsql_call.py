import argparse
import snowflake.connector
import sys

def is_valid_value(val: str) -> bool:
    """
    Returns True if val is not None, not empty, not just whitespace,
    and not one of the common placeholders like 'null' or 'none' (case-insensitive).
    """
    if val is None:
        return False

    stripped_val = val.strip()
    if not stripped_val:
        return False

    if stripped_val.lower() in ("null", "none"):
        return False
    
    return True

def parse_config_file(file_path: str) -> dict:
    config = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()

    return config

def main():
    parser = argparse.ArgumentParser(
        description="Parse config.txt for a specific environment section (e.g., [UAT])"
    )
    parser.add_argument("--config-file", required=True, help="Path to your config.txt")
    parser.add_argument("--secret-file", required=True, help="Path to your secrets.txt")
    args = parser.parse_args()

    # Read credentials from config file
    config = parse_config_file(args.config_file)
    secret = parse_config_file(args.secret_file)

    # Extract required fields
    account    = secret.get('snowflakeAccount')
    username   = secret.get('snowflakeUsername')
    password   = secret.get('snowflakePassword')
    role       = config.get('snowflakeRole')
    warehouse  = config.get('snowflakeWarehouse')
    database   = config.get("snowflakeDatabase")
    schema     = config.get("snowflakeSchema")

    # Validate secret file fields
    if not all(is_valid_value(x) for x in [account, username, password]):
        print("Error: Missing or invalid Snowflake configuration values in secret.txt")
        sys.exit(1)
        return  # <-- ensures no further code runs in tests

    # Validate config file fields
    if not all(is_valid_value(x) for x in [role, warehouse, database, schema]):
        print("Error: Missing or invalid Snowflake configuration values in config.txt")
        sys.exit(1)
        return  # <-- ensures no further code runs in tests

    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            account   = account,
            user      = username,
            password  = password,
            role      = role,
            warehouse = warehouse,
            database  = database,
            schema    = schema
        )
        print("Successfully connected to Snowflake.")

        # Example usage:
        cur = conn.cursor()
        try:
            # Apply row access policy
            # Think if you want to make it generic from a file or passed like argument
            cur.execute("")
            print("Row access policies for Catalyst are applied successfully")
        finally:
            cur.close()
    except Exception as ex:
        print(f"Failed to connect to Snowflake: {ex}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()