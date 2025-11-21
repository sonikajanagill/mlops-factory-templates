import base64
import json
import os
import requests
import google.auth
from google.auth.transport.requests import Request

def trigger_dag(event, context):
    """
    Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # 1. Parse Pub/Sub message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    print(f"Received message: {pubsub_message}")
    
    # 2. Get Composer Web Server URL and Client ID from env vars
    web_server_url = os.environ.get('COMPOSER_WEB_SERVER_URL')
    client_id = os.environ.get('COMPOSER_CLIENT_ID')
    dag_id = 'monitoring_drift_retrain'

    if not web_server_url or not client_id:
        print("Error: COMPOSER_WEB_SERVER_URL or COMPOSER_CLIENT_ID not set.")
        return

    # 3. Authenticate
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    auth_req = Request()
    credentials.refresh(auth_req)
    id_token = credentials.id_token

    # 4. Trigger DAG
    endpoint = f"{web_server_url}/api/v1/dags/{dag_id}/dagRuns"
    headers = {
        'Authorization': f'Bearer {id_token}',
        'Content-Type': 'application/json'
    }
    data = {'conf': {'message': pubsub_message}}

    response = requests.post(endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"DAG {dag_id} triggered successfully.")
    else:
        print(f"Error triggering DAG: {response.status_code} - {response.text}")
