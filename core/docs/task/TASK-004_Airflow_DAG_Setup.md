# [TASK-004] Set Up Initial Airflow DAG for Batch Processing

**Status:** `Open`  
**Priority:** `Medium`  
**Owner:** `Project Owner`  
**Assignee:** `Data Engineer`  

---

## 1. Project Owner's Perspective

### Goal
To establish a robust, schedulable, and monitorable system for our recurring batch data pipelines. This will enable us to automate critical offline tasks like model retraining, daily report generation, and large-scale data validation, moving us from manual script execution to a professional orchestration framework.

### User Story
"As a Data Platform Owner, I want to orchestrate our batch jobs using Apache Airflow, so that I can define them as code, schedule them to run automatically, monitor their execution, and easily retry them upon failure."

### Value Proposition
- **Automation:** Eliminates the need for manual execution of batch jobs, reducing operational overhead.
- **Reliability:** Provides robust scheduling, logging, and alerting, ensuring that critical tasks run as expected.
- **Scalability:** Airflow is designed to manage complex dependencies and scale to handle a large number of tasks.
- **Visibility:** The Airflow UI provides a clear view of past and present pipeline runs, making it easy to monitor and debug.
- **Reproducibility:** Pipelines are defined as code (DAGs), making them versionable, reviewable, and reproducible.

### Acceptance Criteria
- An `airflow/dags` directory is created in the project root.
- A simple, functional Airflow DAG is created to serve as a template.
- The DAG must successfully execute a `BashOperator` that calls an existing Python script within the DAFU project.
- The DAG is scheduled to run (e.g., daily).
- Instructions on how to run Airflow locally for development are documented.

---

## 2. Technical Analysis & Implementation Plan

### Current State
The project's `README.md` explicitly mentions Apache Airflow as a planned tool for orchestrating scheduled jobs. Currently, any batch processing would have to be triggered by manually running a Python script. There is no scheduler or orchestrator.

### Proposed Solution
We will introduce Apache Airflow by creating a dedicated directory for DAGs and implementing a simple "hello world" style DAG that demonstrates how to call our existing project scripts. This provides a foundation and a pattern for all future data pipelines.

### Step-by-Step Implementation
1.  **Add Dependency:** Add `apache-airflow` to the `requirements.txt` file. It's recommended to use constraints for reproducible builds: `pip install "apache-airflow[cncf.kubernetes,docker,postgres,redis,ssh,statsd]==2.8.1" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.9.txt"`.
2.  **Create Directory Structure:** In the project root, create a new directory structure: `airflow/dags`. This is the standard location where Airflow looks for DAG files.
3.  **Create the First DAG:** Inside `airflow/dags`, create a new Python file named `example_daily_fraud_report_dag.py`.
4.  **Define the DAG:** In the new file, define a simple DAG.
    - Import necessary modules: `DAG`, `datetime`, `BashOperator`.
    - Define default arguments (e.g., `owner`, `start_date`, `retries`).
    - Instantiate the `DAG` with a unique `dag_id`, a `schedule_interval` (e.g., `@daily`), and the default arguments.
    - **Important:** The `BashOperator` command must be carefully constructed. It needs to activate the project's virtual environment and then call the target Python script with the correct path.
      ```python
      import pendulum
      from airflow.models.dag import DAG
      from airflow.operators.bash import BashOperator
      
      # Define the path to the project and the script to run
      PROJECT_ROOT = "/opt/airflow/path/to/your/project/dafu" # This path needs to be correct inside the Airflow worker
      VENV_ACTIVATE = f"source {PROJECT_ROOT}/core/features/fraud_detection/venv/bin/activate"
      SCRIPT_TO_RUN = f"python {PROJECT_ROOT}/core/features/fraud_detection/src/models/main.py"

      with DAG(
          dag_id="daily_fraud_report_example",
          start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
          schedule="@daily",
          catchup=False,
          tags=["example"],
      ) as dag:
          t1 = BashOperator(
              task_id="run_fraud_detection_script",
              bash_command=f"echo 'Activating venv and running script...' && {VENV_ACTIVATE} && {SCRIPT_TO_RUN}",
          )
      ```
5.  **Document Local Setup:** Add a new document, `core/docs/guides/AIRFLOW_SETUP.md`. This document must explain how a developer can run Airflow locally to test their DAGs. The recommended method is to use the official Airflow Docker Compose file:
    - Instruct the user to download the file: `curl -LfO "https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml"`
    - Explain that they need to create `.env`, `logs`, `plugins` directories.
    - Explain how to mount the project's `airflow/dags` directory into the Airflow services by modifying the `docker-compose.yaml` volumes.
    - Provide the command to start Airflow: `docker-compose up -d`.

### Key Files & Directories to Modify
- `/requirements.txt` (Add `apache-airflow`)
- `/airflow/dags/` (New directory)
- `/airflow/dags/example_daily_fraud_report_dag.py` (New file)
- `/core/docs/guides/AIRFLOW_SETUP.md` (New file)

### Testing Strategy
- **DAG Validation:** Once Airflow is running locally, the Airflow UI will automatically parse the new DAG file. Check the UI for any DAG import errors.
- **Manual Trigger:** From the Airflow UI, manually trigger the `daily_fraud_report_example` DAG.
- **Log Inspection:** Check the logs for the `run_fraud_detection_script` task in the Airflow UI. Verify that the output shows the script being executed and that it completes without errors.
- **Task Failure Test:** Modify the `bash_command` to point to a non-existent script and verify that the task fails as expected in the Airflow UI.

---
## 2.1. Deep Dive: Engineering Perspective

### Beyond `BashOperator`: The TaskFlow API and Providers
While `BashOperator` is a great starting point, it tightly couples our orchestration logic to shell commands and file paths. A more robust and maintainable approach is to use provider-specific operators and the TaskFlow API.

- **TaskFlow API:** By using the `@task` decorator, we can turn Python functions directly into Airflow tasks. This allows for cleaner, more readable DAGs and makes passing data between tasks (via automatic XComs) trivial.

- **Provider Packages:** Instead of using `BashOperator` to run a `psql` command, we should install the `apache-airflow-providers-postgres` package. This gives us access to the `PostgresOperator`, which can execute SQL directly against a configured Postgres connection. This is more secure and more explicit.

**Revised Example:**
```python
from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
import pendulum

@dag(
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
)
def fraud_etl_dag():
    
    @task
    def extract_data() -> str:
        # Python logic to extract data, returns a file path
        return "/tmp/extracted_data.csv"

    # Use a provider operator to interact with a database
    run_postgres_query = PostgresOperator(
        task_id="run_sql_transformation",
        postgres_conn_id="dafu_postgres_conn", # ID from Airflow Connections
        sql="CALL process_daily_transactions();",
    )

    extracted_path = extract_data()
    # ... subsequent tasks can use the output of extract_data()

fraud_etl_dag()
```

### Connection Management
Secrets like database connection strings should **never** be hardcoded in a DAG file. The correct practice is to use Airflow's built-in **Connections** manager (Admin -> Connections in the UI). We would create a new connection, give it an ID (e.g., `dafu_postgres_conn`), and securely store the host, username, and password there. Our DAGs then reference this connection by its ID, abstracting away the credentials.

### Idempotency: The Cornerstone of Reliable Pipelines
Every task in our DAGs must be **idempotent**. This means that running the same task multiple times with the same input should produce the exact same result. This is critical for recovery after failures. If a task fails halfway through a DAG run, we need to be able to re-run it without creating duplicate data or causing other side effects.

**Example of non-idempotent task:** `INSERT INTO table ...` (will create duplicates if re-run).
**Example of idempotent task:** `INSERT INTO table ... ON CONFLICT (id) DO UPDATE SET ...` (will insert or update, but not duplicate).

All our data processing logic, whether in SQL or Python, must be designed with idempotency in mind from the start.
