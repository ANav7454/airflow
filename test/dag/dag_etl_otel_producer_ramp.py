from airflow import DAG
from airflow.operators.python import PythonOperator


from influxdb_client import InfluxDBClient
import pandas as pd
import re
from datetime import datetime, timedelta
import os
import psycopg2
import pytz

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'sync_influxdb_to_postgres',
    default_args=default_args,
    description='Sync InfluxDB to PostgreSQL',
    schedule_interval=timedelta(minutes=1),
)

def ingest():
    '''Ingest data from InfluxDB2'''
    print('task_ingest')

def transform():
    '''Transform data'''
    print('task_transform')

def Load():
    '''Load datta to PostgreSQL'''
    print('task_load')    

task_1 = PythonOperator(
 task_id='task_1',
 python_callable=ingest,
 dag=dag,
)

task_2 = PythonOperator(
 task_id='task_2',
 python_callable=transform,
 dag=dag,
)

task_3 = PythonOperator(
 task_id='task_3',
 python_callable=Load,
 dag=dag,
)

task_1 >> task_2 >> task_3



