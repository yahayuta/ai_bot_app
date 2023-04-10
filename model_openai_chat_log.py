from google.cloud import bigquery

# save chat log into bigquery
def save_log(user_id, role, msg):
    client = bigquery.Client()
    client.query(f'INSERT INTO app.openai_chat_log(user_id,chat,role,created) values(\'{user_id}\',\'\'\'{msg}\'\'\',\'{role}\',CURRENT_DATETIME(\'Asia/Tokyo\'))')

# load chat log from bigquery
def get_logs(user_id):
    client = bigquery.Client()
    query_job = client.query(f'SELECT * FROM app.openai_chat_log where user_id = \'{user_id}\' order by created;')
    rows = query_job.result()
    print(rows.total_rows)
    logs = []
    for row in rows:
        log = {"role": row["role"], "content": row["chat"]}
        logs.append(log)
    return logs

# delete all chat log from bigquery
def delete_logs(user_id):
    client = bigquery.Client()
    client.query(f'DELETE FROM app.openai_chat_log where user_id = \'{user_id}\';')