import argparse
import snowflake.connector
import sys

def parse_config_file(file_path: str, env: str) -> dict:
    config = {}
    in_section = False
    section_header = f"[{env}]"

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # If we encounter a bracketed line like [UAT] or [DEV], check if it's our env
            if line.startswith('[') and line.endswith(']'):
                if line == section_header:
                    in_section = True  # Start capturing
                else:
                    in_section = False  # We've hit a different section, stop capturing
                continue

            # If we're in the right section, capture key=value lines
            if in_section and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()

    return config

def main():
    parser = argparse.ArgumentParser(
        description="Parse config.txt for a specific environment section (e.g., [UAT])"
    )
    parser.add_argument("--config-file", required=True, help="Path to your config.txt")
    parser.add_argument("--env", help="Which environment section to parse. Choose between QA | UAT | PROD.")
    parser.add_argument("--schema", help="Which schema.")
    args = parser.parse_args()

    # Read credentials from config file
    config = parse_config_file(args.config_file, args.env)

    # Extract required fields
    account    = config.get('snowflakeAccount')
    username   = config.get('snowflakeUsername')
    password   = config.get('snowflakePassword')
    role       = config.get('snowflakeRole')
    warehouse  = config.get('snowflakeWarehouse')

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
            database  = args.env,
            schema    = args.schema
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