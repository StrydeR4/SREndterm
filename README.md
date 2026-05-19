# MicroShop — SRE End Term Project

## Services

| Service | Port | Description |
|---|---|---|
| Frontend | 80 | Nginx-based web dashboard |
| Auth Service | 8001 | User authentication |
| Product Service | 8002 | Product catalog |
| Order Service | 8003 | Order processing (PostgreSQL) |
| User Service | 8004 | User profiles and chat |
| Payment Service | 8005 | Payment simulation |
| Notification Service | 8006 | Email/SMS/Push notifications |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3005 | Monitoring dashboards |

## Quick Start (Docker Compose)

docker-compose up --build -d
```

Open http://localhost in your browser.

- Grafana: http://localhost:3005 (admin/admin)
- Prometheus: http://localhost:9090

## Docker Swarm

docker swarm init
docker stack deploy -c docker-stack.yml microshop
docker stack ps microshop
```

## Kubernetes

kubectl apply -f kubernetes/namespace.yml
kubectl apply -f kubernetes/configmap.yml
kubectl apply -f kubernetes/postgres.yml
kubectl apply -f kubernetes/auth-service.yml
kubectl apply -f kubernetes/services.yml
kubectl apply -f kubernetes/order-service.yml
kubectl apply -f kubernetes/frontend.yml
kubectl get pods -n microshop
```
## Ansible Deployment

# Edit ansible/inventory.ini with your server IP
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

## Terraform Infrastructure

cd terraform
terraform init
terraform plan
terraform apply
```

## Load Testing

pip install aiohttp
python load_test.py
```

## Incident Simulation

In `docker-compose.yml` change `DB_HOST: postgres` to `DB_HOST: wrong-host`:

docker-compose up -d --no-deps order-service
# Watch Health tab and Grafana for errors
# Then fix and restore:
docker-compose up -d --no-deps order-service
```

## SLI/SLO

| SLI | SLO | Measurement |
|---|---|---|
| Availability | >= 99% | up metric in Prometheus |
| Latency | <= 200ms | product_request_duration_seconds |
| Error rate | <= 1% | order_errors_total / orders_total |
| Login success | >= 95% | auth_login_total{status="success"} |
