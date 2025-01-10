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
driver_opennebula = Entity(name="metrics_edge", join_keys=["one_vm_name"])
driver_stats_source_opennebula = PostgreSQLSource(
    name="metrics__service_opennebula",
    query='''SELECT
            holo._time,
            holo.one_vm_name,
            holo.one_vm_worker,
            holo.orchestrator_cloud_k8s_pod_cpu_utilization_mean ,
            holo.orchestrator_media_k8s_pod_cpu_utilization_mean ,
            holo.orchestrator_cloud_k8s_pod_cpu_utilization_min ,
            holo.orchestrator_media_k8s_pod_cpu_utilization_min ,
            holo.orchestrator_cloud_k8s_pod_cpu_utilization_max ,
            holo.orchestrator_media_k8s_pod_cpu_utilization_max ,
            k8s.opennebula_k8s_container_cpu_limit,
            k8s.opennebula_k8s_container_cpu_request,
            k8s.opennebula_k8s_node_allocatable_cpu,
            k8s.opennebula_k8s_node_cpu_utilization,
            libvirt.opennebula_libvirt_cpu_seconds_total,
            libvirt.opennebula_libvirt_cpu_system_seconds_total,
            libvirt.opennebula_libvirt_cpu_user_seconds_total,
            libvirt.opennebula_libvirt_vcpu_maximum,
            libvirt.opennebula_libvirt_vcpu_online,
            libvirt.opennebula_libvirt_vcpu_state,
            libvirt.opennebula_libvirt_vcpu_time_seconds_total,
            libvirt.opennebula_libvirt_vcpu_wait_seconds_total
        FROM
            metrics_holo_k8s_1m AS holo
        INNER JOIN
            metrics_opennebula_libvirt_1m AS libvirt
        ON
            holo._time = libvirt._time AND holo.one_vm_worker = libvirt.one_vm_worker
        INNER JOIN
            metrics_opennebula_k8s_1m AS k8s
        ON
            holo._time = k8s._time AND holo.one_vm_name = k8s.one_vm_name
        ''',
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
        Field(name="orchestrator_cloud_k8s_pod_cpu_utilization", dtype=Float32),
        Field(name="orchestrator_media_k8s_pod_cpu_utilization", dtype=Float32),
        Field(name="opennebula_k8s_container_cpu_limit", dtype=Float32),
        Field(name="opennebula_k8s_container_cpu_request", dtype=Float32),
        Field(name="opennebula_k8s_node_allocatable_cpu", dtype=Float32),
        Field(name="opennebula_k8s_node_cpu_utilization", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_system_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_cpu_user_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_vcpu_maximum", dtype=Float32),
        Field(name="opennebula_libvirt_vcpu_online", dtype=Float32),
        Field(name="opennebula_libvirt_vcpu_state", dtype=Float32),
        Field(name="opennebula_libvirt_vcpu_time_seconds_total", dtype=Float32),
        Field(name="opennebula_libvirt_vcpu_wait_seconds_total", dtype=Float32)
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