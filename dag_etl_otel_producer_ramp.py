from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import psycopg2
from influxdb_client import InfluxDBClient
import pytz

def sync_influxdb_to_postgres():
    # Configuración de la conexión a InfluxDB
    # Configuración de la conexión a InfluxDB
    url = os.getenv("INFLUXDB_URL","http://influx_DB2:8086")
    token = os.getenv("INFLUXDB_TOKEN","KCbXUjsNG5ko_FVIa9vx2d9oS-WavbGP1I50UZ6xPN1Okzx6FIwZ3Az4GdTjq1B0v0dxbDR8lLS-u-Uq0Byj8A==")  
    org = os.getenv("INFLUXDB_ORG","test")
    bucket = os.getenv("INFLUXDB_BUCKET","test")

    # Configuración de la conexión a PostgreSQL
    pg_host = "postgres_offline2"
    pg_port = '5433'
    pg_database = "postgres"
    pg_user = "feast"
    pg_password = "feast"
    pg_table = 'otel_producer_ramp'
     
    # Inicializa la conexión a InfluxDB 2.x
    client = InfluxDBClient(url=url, token=token, org=org)

    # Inicializa la conexión a PostgreSQL
    pg_conn = psycopg2.connect(host=pg_host, database=pg_database, user=pg_user, password=pg_password)
    pg_cursor = pg_conn.cursor()

    # Asegúrate de que la tabla exista en PostgreSQL
    pg_cursor.execute('''
        CREATE TABLE IF NOT EXISTS otel_producer_ramp (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ NOT NULL,
        host TEXT NOT NULL,
        job TEXT NOT NULL,
        value DOUBLE PRECISION NOT NULL,
        measurement TEXT NOT NULL,
        UNIQUE(timestamp, host, job));
        ''')
    pg_conn.commit()

    # Obtener la última marca de tiempo de sincronización de PostgreSQL
    pg_cursor.execute('SELECT MAX(timestamp) FROM otel_producer_ramp;')
    last_sync_time = pg_cursor.fetchone()[0]

    # Si nunca se han sincronizado datos, establecer una fecha de inicio por defecto
    if last_sync_time is None:
        last_sync_time = datetime(1970, 1, 1, tzinfo=pytz.UTC)

    # Define y ejecuta la consulta Flux
    query = f'''
        from(bucket: "{bucket}")
        |> range(start: {last_sync_time.isoformat()})
        |> filter(fn: (r) => r["_measurement"] == "otel_producer_ramp")
        |> filter(fn: (r) => r["_field"] == "gauge")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''
    query_api = client.query_api()
    result = query_api.query_data_frame(query=query, org=org)

    # Procesa el DataFrame resultante para insertar en PostgreSQL
    if not result.empty:
        for index, row in result.iterrows():
            timestamp = row['_time']
            host = row['host']
            job = row['job']
            value = row['gauge']
            measurement = row['_measurement']

            # Insertar datos en PostgreSQL
            insert_query = '''
                INSERT INTO otel_producer_ramp (timestamp, host, job, value, measurement)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (timestamp, host, job) DO NOTHING;
            '''
            pg_cursor.execute(insert_query, (timestamp, host, job, value, measurement))

        pg_conn.commit()

    pg_cursor.close()
    pg_conn.close()
    client.close()


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
    description='A simple DAG to sync data from InfluxDB to PostgreSQL',
    schedule_interval=timedelta(minutes=30),
)

sync_task = PythonOperator(
    task_id='sync_influxdb_postgres',
    python_callable=sync_influxdb_to_postgres,
    dag=dag,
)
