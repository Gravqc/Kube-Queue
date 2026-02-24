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

---

# 🚀 Running KubeQueue Locally

This section describes how to start the full system from scratch on a clean machine.

---

## 1️⃣ Create the Kind Cluster (Multi-Node Kubernetes)

```bash
kind create cluster --name kubequeue --config kind-config.yaml
```

### What’s happening?

* Creates a 3-node Kubernetes cluster

  * 1 Control Plane
  * 2 Worker Nodes
* Maps host port `8080` → cluster NodePort `30080`
* Enables external traffic into the cluster

Verify:

```bash
kubectl get nodes
```

All nodes should be `Ready`.

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

* Installs NGINX inside the cluster
* Acts as an HTTP reverse proxy
* Routes external traffic to internal services

---

## 3️⃣ Expose Ingress via Fixed NodePort (30080)

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

* Converts Ingress service to NodePort
* Exposes port `30080` inside cluster
* `kind-config.yaml` maps:

  ```
  cluster:30080 → host:8080
  ```

So traffic flow becomes:

```
localhost:8080 → Ingress → Service → Pod
```

---

## 4️⃣ Install Metrics Server (Required for HPA)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Patch it for Kind:

```bash
kubectl patch deployment metrics-server \
  -n kube-system \
  --type='json' \
  -p='[
    {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},
    {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-preferred-address-types=InternalIP"}
  ]'
```

Verify metrics:

```bash
kubectl top nodes
kubectl top pods -A
```

### What’s happening?

* Enables CPU/memory metrics collection
* Required for Horizontal Pod Autoscaler
* Allows Kubernetes to scale based on real resource usage

---

## 5️⃣ Create Application Namespace

```bash
kubectl create namespace kubequeue
```

### Why?

* Logical isolation
* Clean separation from system components

---

## 6️⃣ Build the Docker Image

```bash
docker build -t kubequeue_api:local ./api
```

### What’s happening?

* Containerizes the FastAPI app
* Produces image `kubequeue_api:local`

---

## 7️⃣ Load Image Into Kind

```bash
kind load docker-image kubequeue_api:local --name kubequeue
```

### Why is this required?

Kind nodes are Docker containers.

They **cannot access local images automatically**.

This command injects the image into cluster nodes.

---

## 8️⃣ Deploy Application to Kubernetes

```bash
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-ingress.yaml
kubectl apply -f k8s/api-hpa.yaml
```

### What’s happening?

* Deployment → creates pods (replicas)
* Service → provides stable internal networking
* Ingress → exposes service externally
* HPA → enables automatic scaling based on CPU

Verify:

```bash
kubectl get pods -n kubequeue
kubectl get svc -n kubequeue
kubectl get ingress -n kubequeue
kubectl get hpa -n kubequeue
```

---

## 9️⃣ Configure Local Hostname

Add to `/etc/hosts`:

```
127.0.0.1 kubequeue.local
```

### Why?

Ingress routes using the Host header.

This maps:

```
kubequeue.local → localhost
```

---

## 🔟 Test the Application

```bash
curl -H "Host: kubequeue.local" http://localhost:8080/health
```

Expected:

```json
{"status":"ok","hostname":"kubequeue-api-xxxxx"}
```

---

# 📈 Testing Autoscaling

Generate load:

```bash
while true; do curl -s -H "Host: kubequeue.local" http://localhost:8080/health > /dev/null; done
```

In another terminal:

```bash
kubectl get hpa -n kubequeue -w
```

You should see:

```
REPLICAS: 2 → 3 → 4 ...
```

Kubernetes automatically:

* Detects high CPU
* Creates new pods
* Schedules across worker nodes
* Ingress load-balances traffic

---

# 🧠 Full Request Flow

```
Browser / curl
        ↓
localhost:8080
        ↓
Kind NodePort (30080)
        ↓
NGINX Ingress Controller
        ↓
ClusterIP Service
        ↓
One of the API Pods
        ↓
Response
```

When CPU increases:

```
HPA → Deployment → More Pods → Scheduler → Worker Nodes
```

---

# 🧹 Cleanup

```bash
kind delete cluster --name kubequeue
```

---

# 🎯 What This Setup Demonstrates

* Multi-node Kubernetes cluster
* Control plane vs worker nodes
* Pod scheduling across nodes
* Deployments & ReplicaSets
* Resource requests & limits
* Liveness & readiness probes
* ClusterIP services & internal DNS
* Ingress-based external routing
* NodePort networking in local clusters
* Metrics Server integration
* Horizontal Pod Autoscaling
* Automatic load balancing across replicas

---
