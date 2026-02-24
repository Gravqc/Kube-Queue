# KubeQueue

KubeQueue is a distributed task processing system built to practice hands-on Kubernetes infrastructure concepts using a local multi-node Kind cluster.

The project focuses on deploying and managing a small microservice architecture consisting of:

A FastAPI service for submitting tasks

Background worker pods for asynchronous processing

Redis as a message broker

PostgreSQL with persistent storage

Kubernetes-native constructs such as Deployments, Services, Ingress, Persistent Volumes, Horizontal Pod Autoscaling, and CronJobs

The primary goal of this project is to gain practical experience with production-style Kubernetes workflows including pod lifecycle management, scaling strategies, service discovery, health checks, and infrastructure debugging.

Prerequisities:
- Docker 
- Kubectl - CLI commands for k8s cluster
- Kind - Local K8s cluset using docker containers as nodes

## Local Kubernetes Setup

This project runs on a local multi-node Kubernetes cluster using Kind.

Cluster configuration:

1 Control Plane node

2 Worker nodes

Created using:
```
kind create cluster --name kubequeue --config kind-config.yaml
```

This setup was used to explore:

- Pod scheduling across nodes
- Replica scaling
- Node failure simulation
- Self-healing behavior

Control plane vs worker node responsibilities

