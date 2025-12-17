# Deployment Guide

## Production Deployment

This guide covers deploying the Classroom Engagement System to production environments.

## Pre-Deployment Checklist

- [ ] All tests pass (`pytest test_engagement_system.py`)
- [ ] Docker images build successfully
- [ ] Environment variables configured
- [ ] Database migrations complete
- [ ] SSL certificates ready
- [ ] Monitoring setup
- [ ] Backup strategy defined

## Deployment Options

### Option 1: Docker Compose (Small to Medium)

**Best for**: Single-server deployments, prototypes

#### Setup

1. **Prepare Server**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
```

2. **Clone & Configure**
```bash
git clone <repo-url>
cd classroom-engagement-system
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit .env files with production values
nano backend/.env
nano frontend/.env
```

3. **Configure Production .env**
```bash
# backend/.env
MONGODB_URL=mongodb://root:strongpassword@mongodb:27017/classroom?authSource=admin
REDIS_URL=redis://:strongpassword@redis:6379
CELERY_BROKER_URL=redis://:strongpassword@redis:6379
CELERY_RESULT_BACKEND=redis://:strongpassword@redis:6379
DEBUG=False
```

4. **Update docker-compose.yml**
```yaml
# Add environment variables and security settings
services:
  mongodb:
    environment:
      MONGO_INITDB_ROOT_PASSWORD: <strong-password>
    volumes:
      - mongodb_data:/data/db
    networks:
      - classroom-network
  
  redis:
    command: redis-server --requirepass <strong-password>
    networks:
      - classroom-network
```

5. **Deploy**
```bash
docker-compose up -d
docker-compose logs -f
```

6. **Verify**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "..."}
```

### Option 2: AWS ECS (Scalable, Managed)

#### Architecture
```
ALB (Load Balancer)
├── FastAPI Task (3 instances)
├── React Task (2 instances)
├── Celery Worker Task (5 instances)
└── RDS (MongoDB) + ElastiCache (Redis)
```

#### Deployment Steps

1. **Create ECR Repositories**
```bash
aws ecr create-repository --repository-name classroom-fastapi
aws ecr create-repository --repository-name classroom-react
aws ecr create-repository --repository-name classroom-celery
```

2. **Build & Push Images**
```bash
# Build and tag images
docker build -t classroom-fastapi:latest backend/
docker build -t classroom-react:latest frontend/

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker tag classroom-fastapi:latest $ECR_URI/classroom-fastapi:latest
docker push $ECR_URI/classroom-fastapi:latest
# Repeat for other services
```

3. **Create ECS Cluster**
```bash
aws ecs create-cluster --cluster-name classroom-cluster

# Register task definitions
aws ecs register-task-definition --cli-input-json file://fastapi-task-def.json
aws ecs register-task-definition --cli-input-json file://celery-task-def.json
aws ecs register-task-definition --cli-input-json file://react-task-def.json
```

4. **Create Services**
```bash
aws ecs create-service \
  --cluster classroom-cluster \
  --service-name fastapi-service \
  --task-definition fastapi-task:1 \
  --desired-count 3 \
  --load-balancers targetGroupArn=<ALB-TG-ARN>,containerName=fastapi,containerPort=8000
```

5. **Setup Auto-Scaling**
```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name classroom-asg \
  --launch-configuration classroom-lc \
  --min-size 3 \
  --max-size 10 \
  --desired-capacity 5
```

### Option 3: Kubernetes (Enterprise)

#### Helm Chart Structure
```
classroom-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment-fastapi.yaml
│   ├── deployment-celery.yaml
│   ├── deployment-react.yaml
│   ├── statefulset-mongodb.yaml
│   ├── deployment-redis.yaml
│   ├── service-fastapi.yaml
│   ├── service-react.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secret.yaml
```

#### Install Kubernetes Cluster

1. **Create K8s Cluster** (GKE example)
```bash
gcloud container clusters create classroom-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2
```

2. **Install Helm Chart**
```bash
helm repo add classroom ./classroom-chart
helm install classroom-release ./classroom-chart \
  --namespace production \
  --values values-prod.yaml
```

3. **Verify Deployment**
```bash
kubectl get pods -n production
kubectl get services -n production
kubectl logs -n production deployment/fastapi-deployment
```

#### Example K8s Deployment (fastapi-deployment.yaml)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: classroom-fastapi:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MONGODB_URL
          valueFrom:
            secretKeyRef:
              name: classroom-secrets
              key: mongodb-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: classroom-secrets
              key: redis-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Option 4: Cloud Run (Google Cloud)

#### Deployment Steps

1. **Build Container**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/classroom-fastapi:latest backend/
```

2. **Deploy FastAPI**
```bash
gcloud run deploy classroom-fastapi \
  --image gcr.io/PROJECT_ID/classroom-fastapi:latest \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --timeout 3600 \
  --set-env-vars MONGODB_URL=$MONGODB_URL,REDIS_URL=$REDIS_URL
```

3. **Deploy React**
```bash
gcloud run deploy classroom-frontend \
  --image gcr.io/PROJECT_ID/classroom-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Security Configuration

### SSL/TLS Certificate

```bash
# Using Let's Encrypt with Nginx
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d yourdomain.com
```

### Nginx Configuration
```nginx
upstream fastapi {
    server fastapi:8000;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    
    location /api/ {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location / {
        proxy_pass http://react:3000;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Environment Variables Security

Store secrets in:
- AWS Secrets Manager
- Google Cloud Secret Manager
- HashiCorp Vault
- Kubernetes Secrets

Never commit `.env` files!

## Database Backup & Recovery

### MongoDB Backup

```bash
# Automated daily backup
0 2 * * * /usr/local/bin/backup-mongodb.sh

# Backup script
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="mongodb://root:password@localhost:27017/classroom?authSource=admin" \
  --out="$BACKUP_DIR/classroom_$DATE"
# Upload to S3, GCS, etc.
```

### MongoDB Restore

```bash
mongorestore --uri="mongodb://root:password@localhost:27017" \
  --archive=backup.archive
```

## Monitoring & Logging

### Prometheus Setup

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['localhost:8000']
```

### Logging

```python
# Add to FastAPI main.py
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

### ELK Stack (Elasticsearch, Logstash, Kibana)

```bash
# Filebeat configuration
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/classroom/*.log

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Performance Optimization

### Database Indexing

```javascript
// MongoDB indexes
db.meetings.createIndex({ "meeting_id": 1 }, { unique: true })
db.meetings.createIndex({ "created_at": -1 })
db.meetings.createIndex({ "source_type": 1 })
db.meetings.createIndex({ "engagement_score": -1 })
```

### Caching

```python
# Redis caching
from functools import wraps
import redis

cache = redis.Redis(host='localhost', port=6379)

def cached(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = cache.get(key)
            if result:
                return json.loads(result)
            result = await func(*args, **kwargs)
            cache.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### CDN Configuration

```bash
# Cloudflare or similar
# Cache static assets (frontend)
# Enable compression
# Add caching headers
```

## Health Checks & Monitoring

### FastAPI Health Endpoint

```python
@app.get("/health")
async def health_check():
    try:
        # Check MongoDB
        await mongodb_client.admin.command('ping')
        # Check Redis
        redis_client.ping()
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 503
```

### Automated Alerting

```yaml
# Alert rules
groups:
- name: classroom
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{job="fastapi", status=~"5.."}[5m]) > 0.05
    annotations:
      summary: "High error rate detected"
  
  - alert: CeleryWorkerDown
    expr: up{job="celery"} == 0
    annotations:
      summary: "Celery worker is down"
```

## Rollback Strategy

### Blue-Green Deployment

```bash
# Deploy to green environment
docker-compose -f docker-compose.green.yml up -d

# Run tests
pytest integration_tests/

# Switch traffic (update load balancer)
# If issues, rollback: switch back to blue
```

### Canary Deployment

```bash
# Deploy to 10% of users
kubectl patch service classroom-frontend \
  -p '{"spec":{"trafficPolicy":{"canary":{"weight":10}}}}'

# Monitor metrics
# Gradually increase: 25%, 50%, 100%
```

## Disaster Recovery Plan

### RTO/RPO Targets
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 1 hour

### Backup Strategy
- Daily automated backups
- Weekly snapshots
- Monthly archives (long-term storage)
- Test restores quarterly

### Incident Response
1. **Immediate**: Failover to backup systems
2. **Investigation**: Root cause analysis
3. **Communication**: Notify stakeholders
4. **Recovery**: Restore from backups
5. **Post-Incident**: Update procedures

## Performance Benchmarks

| Component | Metric | Target |
|-----------|--------|--------|
| API Response | p99 latency | < 200ms |
| Diarization | 1-min audio processing | < 1 minute |
| Database | Query p99 | < 50ms |
| Frontend | Load time | < 2s |
| Uptime | Availability | 99.9% |

## Cost Optimization

### Strategies
1. **Right-sizing**: Monitor CPU/memory, adjust instance types
2. **Reserved instances**: Pre-purchase capacity at discount
3. **Spot instances**: Use for non-critical workloads
4. **Auto-scaling**: Scale down during off-peak hours
5. **Database**: Use managed services vs. self-hosted

### Estimated Monthly Costs (AWS)
- ECS Fargate: $200-500
- RDS (MongoDB): $200-400
- ElastiCache (Redis): $50-150
- Load Balancer: $20-30
- Data Transfer: $10-50
- **Total**: ~$500-1,100/month

## Post-Deployment Checklist

- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Backups working
- [ ] Monitoring alerts configured
- [ ] Logs being collected
- [ ] Performance baselines established
- [ ] Load testing completed
- [ ] Team trained on procedures
- [ ] Documentation updated
- [ ] Incident response tested

## Support & Maintenance

### Weekly Tasks
- Review logs for errors
- Monitor performance metrics
- Check backup success

### Monthly Tasks
- Update dependencies
- Review security updates
- Analyze usage trends
- Clean up old data

### Quarterly Tasks
- Test disaster recovery
- Penetration testing
- Capacity planning review
- Cost analysis

---

**For additional help, refer to GETTING_STARTED.md, ARCHITECTURE.md, and README.md**
