from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pymongo import MongoClient
import os

def export_logs():
    mongo_host = os.getenv("MONGO_HOST", "mongo")
    mongo_port = int(os.getenv("MONGO_PORT", 27017))
    client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
    db = client["doc_qa"]

    logs = list(db["logs"].find())
    today_str = datetime.utcnow().strftime("%Y%m%d")

    if logs:
        db[f"logs_archive_{today_str}"].insert_many(logs)
        print(f"✅ Exported {len(logs)} logs to logs_archive_{today_str}")
    else:
        print("⚠️ No logs to export")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
}

with DAG("export_logs_daily",
         default_args=default_args,
         schedule_interval="0 0 * * *",  # Midnight UTC
         catchup=False) as dag:

    task = PythonOperator(
        task_id="export_logs",
        python_callable=export_logs
    )
