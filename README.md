# 🚀 KubeQueue

KubeQueue is a Kubernetes-first project designed to practice real-world infrastructure concepts using a local multi-node cluster powered by Kind.

The focus of this project is not application complexity, but hands-on experience with Kubernetes primitives such as Deployments, Services, scheduling, networking, scaling, and failure recovery.

## 🎯 Current Scope

At this stage, the project includes:

- A containerized FastAPI application
- Kubernetes Deployment with multiple replicas
- Resource requests and limits
- Liveness and readiness probes
- ClusterIP Service for internal networking
- Multi-node cluster (1 control plane + 2 workers)
- Internal DNS-based service discovery
- Load balancing across Pods

The system is deployed inside a local Kind cluster.

## 🏗 Architecture (Current Phase)

Client (inside cluster)
        ↓
ClusterIP Service (kubequeue-api)
        ↓
Multiple API Pods (replicas)
        ↓
Scheduled across Worker Nodes

## 📦 Prerequisites

- Docker
- kubectl (Kubernetes CLI)
- Kind (Kubernetes in Docker)
- Python 3.11+
- Poetry (dependency management)

## ⚙️ Local Kubernetes Setup

Create the multi-node cluster:

kind create cluster --name kubequeue --config kind-config.yaml

Cluster configuration:

1 Control Plane node

2 Worker nodes

Verify:

kubectl get nodes
🐳 Build the Application

From project root:
```
docker build -t kubequeue_api:local ./api
```

Load image into Kind:
```
kind load docker-image kubequeue_api:local --name kubequeue
```
🚀 Deploy to Kubernetes

Apply manifests:
```
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
```

Verify:
```
kubectl get pods -n kubequeue -o wide
kubectl get svc -n kubequeue
```
🔎 Test Internal Service

Run a temporary curl pod inside the cluster:
```
kubectl run curl-test \
  --image=curlimages/curl \
  --rm -it \
  --restart=Never \
  -n kubequeue \
  -- sh
```
Inside the shell:
```
curl http://kubequeue-api/health
```

You should receive:

{"status":"ok"}

If scaled to multiple replicas, requests will be load-balanced across pods.
EX: To see loadbalancing/how requests are forwarded to different replicas/ running pods
```
kubectl scale deployment kubequeue-api --replicas=3 -n kubequeue
```

```
kubectl run curl-test \
  --image=curlimages/curl \
  --rm -it \
  --restart=Never \
  -n kubequeue \
  -- sh

Inside bash
while true; do curl http://kubequeue-api/health; sleep 1; done
```

## 🧠 Infrastructure Concepts Practiced
- Control Plane vs Worker Nodes
- Pod scheduling
- Deployments & ReplicaSets
- Service abstraction
- Internal DNS resolution
- ClusterIP networking
- Resource constraints
- Liveness & readiness probes
- Self-healing behavior