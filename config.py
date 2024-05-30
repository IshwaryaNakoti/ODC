import snowflake.connector
SNOWFLAKE_CONFIG = {
    'account': 'rhtnrmg-ka34159',
    'user': 'ishwaryanakoti',
    'password': 'Ishu@2541',
    'database': 'ODC',
    'schema': 'PUBLIC'
}

def get_connection():
    try:
        return snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    except Exception as e:
        print("An error occurred while connecting to Snowflake:", e)
        return None

SNOWFLAKE_CONNECTOR  = get_connection()