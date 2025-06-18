from google.cloud import bigquery

# save chat log into bigquery
def save_log(user_id, role, message):
    """
    Save a chat log entry to the BigQuery table 'app.chat_log'.

    Args:
        user_id (str): Unique identifier for the user.
        role (str): The role of the message sender (e.g., 'user', 'assistant').
        message (str): The chat message content.

    Returns:
        None
    """
    client = bigquery.Client()
    client.query(f'INSERT INTO app.chat_log(user_id,message,role,created) values(\'{user_id}\',\'\'\'{message}\'\'\',\'{role}\',CURRENT_DATETIME(\'Asia/Tokyo\'))')

# load chat log from bigquery
def get_logs(user_id):
    """
    Retrieve chat logs for a user from BigQuery, formatted for OpenAI API.

    Args:
        user_id (str): Unique identifier for the user.

    Returns:
        list: List of message dicts with 'role' and 'content' keys.
    """
    client = bigquery.Client()
    query_job = client.query(f'SELECT * FROM app.chat_log where user_id = \'{user_id}\' order by created;')
    rows = query_job.result()
    print(rows.total_rows)
    logs = []
    for row in rows:
        log = {"role": row["role"], "content": row["message"]}
        logs.append(log)
    return logs

# load chat log from bigquery for gemini
def get_logs_gemini(user_id):
    """
    Retrieve chat logs for a user from BigQuery, formatted for Gemini API.

    Args:
        user_id (str): Unique identifier for the user.

    Returns:
        list: List of message dicts with 'role' and 'parts' keys.
    """
    client = bigquery.Client()
    query_job = client.query(f'SELECT * FROM app.chat_log where user_id = \'{user_id}\' order by created;')
    rows = query_job.result()
    print(rows.total_rows)
    logs = []
    for row in rows:
        log = {"role": row["role"], "parts": [row["message"]]}
        logs.append(log)
    return logs

# delete all chat log from bigquery
def delete_logs(user_id):
    """
    Delete all chat logs for a user from the BigQuery table 'app.chat_log'.

    Args:
        user_id (str): Unique identifier for the user.

    Returns:
        None
    """
    client = bigquery.Client()
    client.query(f'DELETE FROM app.chat_log where user_id = \'{user_id}\';')