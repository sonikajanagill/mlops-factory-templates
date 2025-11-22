# Multi-Trigger Architecture & Rate Limiting

## The Problem: Redundant Triggers

In a robust MLOps setup, a pipeline might be triggered by multiple sources:

1. **Schedule**: Daily run (e.g., 2 AM).
2. **Event**: New data arrival in GCS.
3. **Manual**: Data Scientist triggering a run.
4. **Monitoring**: Drift detection alert.

Without rate limiting, this can lead to:

* **Race Conditions**: Multiple runs processing the same data.
* **Resource Contention**: Quota exhaustion on Vertex AI or Dataproc.
* **Wasted Cost**: Re-training the model 5 times in an hour because 5 files arrived.

## The Solution: Short-Circuit Rate Limiting

We implement a "check-and-set" pattern using Airflow Variables and the `ShortCircuitOperator`.

### Logic Flow

1. **Get Last Run Time**: Fetch `mlops_last_training_run` from Airflow Variables.
2. **Check Threshold**: If `(Current Time - Last Run) < MIN_HOURS`, skip the pipeline.
3. **Update Last Run**: If proceeding, update `mlops_last_training_run` to the current time.

### Implementation Code

```python
from airflow.operators.python import ShortCircuitOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import logging

def check_rate_limit(**context):
    MIN_HOURS = 5
    last_run_str = Variable.get("mlops_last_training_run", default_var=None)
    
    if not last_run_str:
        logging.info("No previous run recorded. Proceeding.")
        Variable.set("mlops_last_training_run", datetime.now().isoformat())
        return True
        
    last_run = datetime.fromisoformat(last_run_str)
    hours_since_last = (datetime.now() - last_run).total_seconds() / 3600
    
    if hours_since_last < MIN_HOURS:
        logging.warning(f"Rate limit active. Last run was {hours_since_last:.2f} hours ago. Min required: {MIN_HOURS}.")
        return False
        
    logging.info(f"Rate limit passed. Last run was {hours_since_last:.2f} hours ago.")
    Variable.set("mlops_last_training_run", datetime.now().isoformat())
    return True

rate_limit_check = ShortCircuitOperator(
    task_id="check_rate_limit",
    python_callable=check_rate_limit
)
```

## Benefits

* **Cost Savings**: Prevents ~70% of redundant runs in event-driven setups.
* **Stability**: Ensures the system isn't overwhelmed by a flood of events.
* **Control**: Centralized logic to manage pipeline frequency.
