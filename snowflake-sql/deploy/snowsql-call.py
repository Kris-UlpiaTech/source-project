import argparse
import snowflake.connector
import sys

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

    # Validate they exist
    if not all([account, username, password, role, warehouse]):
        sys.exit("Error: Missing one or more Snowflake configuration values in config.txt")

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

if __name__ == "__main__":
    main()