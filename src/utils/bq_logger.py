# bq_logger.py
from google.cloud import bigquery
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger()

PROJECT_ID = "white-defender-496219-d2"
TABLE_ID = f"{PROJECT_ID}.research_assistant.query_logs"

def log_to_bigquery(
    query: str,
    latency_ms: float,
    critique_score: float,
    iterations: int,
    final_answer: str
):
    try:
        client = bigquery.Client(project=PROJECT_ID)
        
        rows = [{
            "query": query,
            "latency_ms": latency_ms,
            "critique_score": critique_score,
            "iterations": iterations,
            "answer_length": len(final_answer),
            "timestamp": datetime.utcnow().isoformat()
        }]
        
        job = client.load_table_from_json(
            rows,
            TABLE_ID,
            job_config=bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND",
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
            )
        )
        job.result()  # wait for job to complete
        
        logger.debug("[+] Query logged to BigQuery successfully.")
    
    except Exception as e:
        logger.error(f"BigQuery logging error: {e}")