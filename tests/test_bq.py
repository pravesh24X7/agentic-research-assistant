from src.utils.bq_logger import log_to_bigquery

log_to_bigquery(
    query="test query from pravesh",
    latency_ms=3400.0,
    critique_score=7.0,
    iterations=1,
    final_answer="this is a test answer to verify bigquery logging works correctly"
)

print("Done — check BigQuery console for the row.")