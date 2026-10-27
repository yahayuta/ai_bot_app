from google.cloud import bigquery


def _params(**values):
    """Build a job config with named STRING parameters, so user input is never spliced into SQL."""
    return bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter(k, "STRING", v) for k, v in values.items()]
    )


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
    client.query(
        "INSERT INTO app.chat_log(user_id, message, role, created) "
        "VALUES (@user_id, @message, @role, CURRENT_DATETIME('Asia/Tokyo'))",
        job_config=_params(user_id=user_id, message=message, role=role),
    )

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
    query_job = client.query(
        "SELECT * FROM app.chat_log WHERE user_id = @user_id ORDER BY created",
        job_config=_params(user_id=user_id),
    )
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
    query_job = client.query(
        "SELECT * FROM app.chat_log WHERE user_id = @user_id ORDER BY created",
        job_config=_params(user_id=user_id),
    )
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
    client.query(
        "DELETE FROM app.chat_log WHERE user_id = @user_id",
        job_config=_params(user_id=user_id),
    )