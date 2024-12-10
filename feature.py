# This is an example feature definition file
from datetime import timedelta
import pandas as pd
from feast import Entity, FeatureService, FeatureView, Field, PushSource, RequestSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Float64, Int64, String
# Define an entity for the driver. You can think of an entity as a primary key used to
# fetch features.
driver_opennebula = Entity(name="metrics_edge", join_keys=["service_id"])
driver_stats_source_opennebula = PostgreSQLSource(
    name="metrics__service_opennebula",
    query="SELECT * FROM metrics_edge",
    timestamp_field="_time",
    #created_timestamp_column="created",
)

metrics_opennebula_view = FeatureView(
    # The unique name of this feature view. Two feature views in a single
    # project cannot have the same name
    name="opennebula_feature",
    entities=[driver_opennebula],
    ttl=timedelta(days=1),
    # The list of features defined below act as a schema to both define features
    # for both materialization of features into a store, and are used as references
    # during retrieval for building a training dataset or serving features
    schema=[
        Field(name="opennebula_libvirt_memory_available_bytes", dtype=Float32),
        Field(name="opennebula_libvirt_memory_maximum_bytes", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_system_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_user_seconds_total", dtype=Float32)
    ],
    online=True,
    source=driver_stats_source_opennebula,
    # Tags are user defined key/value pairs that are attached to each
    # feature view
    #tags={"team": "ramp"},
)
metrics_opennebula_service = FeatureService(
    name="opennebula_feature",
    features=[metrics_opennebula_view]
)