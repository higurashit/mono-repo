from diagrams import Cluster, Diagram

# AWS resources search for https://diagrams.mingrammer.com/docs/nodes/aws

## samples: Static Web Service
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet
from diagrams.aws.security import WAF, ACM
from diagrams.aws.network import CF
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3

with Diagram('Web Service Name'):
    users = Users('End User')
    internet = Internet('Internet')

    with Cluster('AWS'):
        with Cluster('WAF Rules'):
            waf = [WAF('WAF: rules\n同一IPからの連続アクセス遮断'), WAF('WAF: rules\nIP制限（検証環境のみ）')]

        cf = CF('CloudFront\nキャッシュサーバ')

        with Cluster('Lambda@Edge Origin Request'):
            lmd = Lambda('Lambda\nS3 ディレクトリアクセス')

        s3 = S3('S3\n静的コンテンツ置き場')
        acm = ACM('ACM\nSSL証明書')


    users >> internet >> waf >> cf >> lmd >> s3
    acm - cf

## samples: ALL on-premise Icons
from diagrams.onprem.analytics import Beam, Dbt, Flink, Hadoop, Hive, Metabase, Norikra, Singer, Spark, Storm, Tableau
from diagrams.onprem.cd import Spinnaker, Tekton, TektonCli
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.compute import Nomad, Server
from diagrams.onprem.container import Docker, Rkt, RKT
from diagrams.onprem.database import Cassandra, Clickhouse, ClickHouse, Cockroachdb, CockroachDB, Couchbase, Couchdb, CouchDB, Dgraph, Hbase, HBase, Influxdb, InfluxDB, Janusgraph, JanusGraph, Mariadb, MariaDB, Mongodb, MongoDB, Mssql, MSSQL, Mysql, MySQL, Neo4J, Oracle, Postgresql, PostgreSQL, Scylla
from diagrams.onprem.etl import Embulk
from diagrams.onprem.gitops import Argocd, ArgoCD, Flagger, Flux
from diagrams.onprem.iac import Ansible, Awx, Terraform
from diagrams.onprem.inmemory import Aerospike, Hazelcast, Memcached, Redis
from diagrams.onprem.logging import Fluentbit, FluentBit, Fluentd, Loki
from diagrams.onprem.mlops import Polyaxon
from diagrams.onprem.monitoring import Datadog, Grafana, Prometheus, Sentry, Splunk, Thanos
from diagrams.onprem.network import Apache, Caddy, Consul, Envoy, Etcd, ETCD, Haproxy, HAProxy, Internet, Istio, Kong, Linkerd, Nginx, Pfsense, PFSense, Pomerium, Tomcat, Traefik, Vyos, VyOS, Zookeeper
from diagrams.onprem.queue import Activemq, ActiveMQ, Celery, Kafka, Rabbitmq, RabbitMQ, Zeromq, ZeroMQ
from diagrams.onprem.search import Solr
from diagrams.onprem.security import Trivy, Vault
from diagrams.onprem.vcs import Git, Github, Gitlab
from diagrams.onprem.workflow import Airflow, Digdag, Kubeflow, KubeFlow, Nifi, NiFi

with Diagram('Service Name'):
    with Cluster("analytics"):
        Client() - Beam() - Dbt() - Flink() - Hadoop() - Hive() - Metabase() - Norikra() - Singer() - Spark() - Storm() - Tableau()
    with Cluster("cd"):
        Spinnaker() - Tekton() - TektonCli()
    with Cluster("client"):
        Client() - User() - Users()
    with Cluster("compute"):
        Nomad() - Server()
    with Cluster("container"):
        Docker() - Rkt() - RKT()
    with Cluster("database"):
        Cassandra() - Clickhouse() - ClickHouse() - Cockroachdb() - CockroachDB() - Couchbase() - Couchdb() - CouchDB() - Dgraph() - Hbase() - HBase() - Influxdb() - InfluxDB() - Janusgraph() - JanusGraph() - Mariadb() - MariaDB() - Mongodb() - MongoDB() - Mssql() - MSSQL() - Mysql() - MySQL() - Neo4J() - Oracle() - Postgresql() - PostgreSQL() - Scylla()
    with Cluster("etl"):
        Embulk()
    with Cluster("gitops"):
        Argocd() - ArgoCD() - Flagger() - Flux()
    with Cluster("iac"):
        Ansible() - Awx() - Terraform()
    with Cluster("inmemory"):
        Aerospike() - Hazelcast() - Memcached() - Redis()
    with Cluster("logging"):
        Fluentbit() - FluentBit() - Fluentd() - Loki()
    with Cluster("mlops"):
        Polyaxon()
    with Cluster("monitoring"):
        Datadog() - Grafana() - Prometheus() - Sentry() - Splunk() - Thanos()
    with Cluster("network"):
        Apache() - Caddy() - Consul() - Envoy() - Etcd() - ETCD() - Haproxy() - HAProxy() - Internet() - Istio() - Kong() - Linkerd() - Nginx() - Pfsense() - PFSense() - Pomerium() - Tomcat() - Traefik() - Vyos() - VyOS() - Zookeeper()
    with Cluster("queue"):
        Activemq() - ActiveMQ() - Celery() - Kafka() - Rabbitmq() - RabbitMQ() - Zeromq() - ZeroMQ()
    with Cluster("search"):
        Solr()
    with Cluster("security"):
        Trivy() - Vault()
    with Cluster("vcs"):
        Git() - Github() - Gitlab()
    with Cluster("workflow"):
        Airflow() - Digdag() - Kubeflow() - KubeFlow() - Nifi() - NiFi()
