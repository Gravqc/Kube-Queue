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

# 🚀 Running KubeQueue Locally

This section describes how to start the full system from scratch on a clean machine.

---

## 1️⃣ Create the Kind Cluster (K8s)

```bash
kind create cluster --name kubequeue --config kind-config.yaml
```

### What’s happening?

* Creates a multi-node Kubernetes cluster
* 1 control plane node
* 2 worker nodes
* Maps host port `8080` → NodePort `30080`
* Kubernetes control plane becomes accessible via `kubectl`

Verify:

```bash
kubectl get nodes
```

You should see 3 nodes in `Ready` state.

---

## 2️⃣ Install NGINX Ingress Controller (Kind Version)

```bash
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml
```

Wait until:

```bash
kubectl get pods -n ingress-nginx
```

Controller pod should be `Running`.

### What’s happening?

* Installs NGINX inside cluster
* Acts as edge router
* Will route external HTTP traffic to internal services

---

## 3️⃣ Configure Ingress to Use Fixed NodePort

Force ingress to use NodePort `30080`:

```bash
kubectl patch svc ingress-nginx-controller \
  -n ingress-nginx \
  --type='json' \
  -p='[
    {"op":"replace","path":"/spec/type","value":"NodePort"},
    {"op":"replace","path":"/spec/ports/0/nodePort","value":30080}
  ]'
```

### What’s happening?

* Converts ingress service to NodePort
* Exposes port 30080 inside cluster
* Port 30080 maps to `localhost:8080` via Kind config

Traffic path now becomes:

```
localhost:8080 → Ingress → Service → Pod
```

---

## 4️⃣ Create Application Namespace

```bash
kubectl create namespace kubequeue
```

### Why?

* Logical isolation
* Clean separation from system components

---

## 5️⃣ Build the Docker Image

```bash
docker build -t kubequeue_api:local ./api
```

### What’s happening?

* Containerizes FastAPI app
* Produces image `kubequeue_api:local`

---

## 6️⃣ Load Image Into Kind

```bash
kind load docker-image kubequeue_api:local --name kubequeue
```

### Why is this required?

Kind nodes are Docker containers.

They **cannot see your local images automatically**.

This command injects the image into cluster nodes.

---

## 7️⃣ Deploy Application to Kubernetes

```bash
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-ingress.yaml
```

### What’s happening?

* Deployment → creates pods (replicas)
* Service → provides stable internal access
* Ingress → exposes service externally

Verify:

```bash
kubectl get pods -n kubequeue
kubectl get svc -n kubequeue
kubectl get ingress -n kubequeue
```

Pods should be `Running`.

---

## 8️⃣ Configure Local Hostname

Add this to `/etc/hosts`:

```
127.0.0.1 kubequeue.local
```

### Why?

Ingress routes based on Host header.

This makes your browser resolve:

```
kubequeue.local → localhost
```

---

## 9️⃣ Test the Application

```bash
curl -H "Host: kubequeue.local" http://localhost:8080/health
```

Expected output:

```json
{"status":"ok","hostname":"kubequeue-api-xxxxx"}
```

You can also open in browser:

```
http://kubequeue.local:8080/health
```

---

# 🧠 Full Request Flow

When you call the API:

```
Browser
  ↓
localhost:8080
  ↓
Kind NodePort (30080)
  ↓
NGINX Ingress
  ↓
ClusterIP Service
  ↓
One of the API Pods
```

Requests are load-balanced across replicas automatically.

---

# 🧹 Optional: Cleanup

Delete cluster:

```bash
kind delete cluster --name kubequeue
```

---

# 🎯 What This Setup Demonstrates

* Multi-node Kubernetes cluster
* Pod scheduling
* Replica management
* Internal DNS & service discovery
* Liveness & readiness probes
* Ingress-based routing
* NodePort networking in local clusters
* Image management in Kind

---
