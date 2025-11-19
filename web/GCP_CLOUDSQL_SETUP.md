# GCP Cloud SQL Configuration Guide

## Environment Variables Setup

### Option 1: Cloud SQL via Unix Socket (Recommended for Cloud Run/App Engine)

When deploying to GCP Cloud Run or App Engine, use Unix domain sockets:

```bash
# Your Cloud SQL instance connection name
INSTANCE_CONNECTION_NAME=your-project:your-region:your-instance

# Database credentials
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# Optional pool settings
DB_POOL_MAX=10
DB_POOL_IDLE_TIMEOUT=30000
DB_POOL_CONNECT_TIMEOUT=10000

NODE_ENV=production
```

**How to find your connection name:**
```bash
gcloud sql instances describe YOUR_INSTANCE_NAME --format="value(connectionName)"
```

### Option 2: Cloud SQL via Public IP (Local Development)

For local development with Cloud SQL Auth Proxy or public IP:

```bash
# Use localhost when running Cloud SQL Proxy locally
DB_HOST=127.0.0.1
DB_PORT=5432

# Or use the public IP directly
# DB_HOST=34.XXX.XXX.XXX
# DB_PORT=5432

# Database credentials
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

# Legacy variables (for backward compatibility)
PUBLIC_IP=127.0.0.1
USERNAME=your_username
PASSWORD=your_password
DATABASE_NAME=your_database_name

NODE_ENV=development
```

## Running Cloud SQL Auth Proxy Locally

Install the proxy:
```bash
# Download Cloud SQL Auth Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64
chmod +x cloud-sql-proxy
```

Run the proxy:
```bash
# Replace with your instance connection name
./cloud-sql-proxy your-project:your-region:your-instance --port 5432
```

## Cloud Run Deployment Configuration

### 1. Set environment variables in Cloud Run:
```bash
gcloud run services update YOUR_SERVICE_NAME \
  --set-env-vars="INSTANCE_CONNECTION_NAME=your-project:your-region:your-instance" \
  --set-env-vars="DB_USER=your_username" \
  --set-env-vars="DB_NAME=your_database" \
  --set-secrets="DB_PASSWORD=db-password:latest" \
  --add-cloudsql-instances=your-project:your-region:your-instance
```

### 2. Or use Cloud Run YAML configuration:
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: your-service
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cloudsql-instances: your-project:your-region:your-instance
    spec:
      containers:
      - image: gcr.io/your-project/your-image
        env:
        - name: INSTANCE_CONNECTION_NAME
          value: your-project:your-region:your-instance
        - name: DB_USER
          value: your_username
        - name: DB_NAME
          value: your_database
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-password
              key: latest
        - name: NODE_ENV
          value: production
```

## Security Best Practices

1. **Use Secret Manager for passwords:**
   ```bash
   # Create secret
   echo -n "your-password" | gcloud secrets create db-password --data-file=-
   
   # Grant access to service account
   gcloud secrets add-iam-policy-binding db-password \
     --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

2. **Use IAM Database Authentication (Recommended):**
   - No passwords in environment variables
   - Uses Cloud IAM for authentication
   - More secure for production

3. **Private IP Connection:**
   - Use VPC peering for private connections
   - More secure than public IP
   - Lower latency

## Connection Pooling Best Practices

The code automatically sets optimal pool settings:

- **max**: 10 connections (Cloud SQL default connection limit is 25-100)
- **idleTimeoutMillis**: 30 seconds (Cloud SQL has 10-min idle timeout)
- **connectionTimeoutMillis**: 10 seconds

Adjust based on your needs:
```bash
DB_POOL_MAX=20
DB_POOL_IDLE_TIMEOUT=60000
DB_POOL_CONNECT_TIMEOUT=15000
```

## Testing the Connection

Test locally with Cloud SQL Proxy:
```bash
# Terminal 1: Run proxy
./cloud-sql-proxy your-project:your-region:your-instance --port 5432

# Terminal 2: Test connection
psql "host=127.0.0.1 port=5432 user=your_user dbname=your_db"

# Terminal 3: Run your app
npm start
```

## Troubleshooting

### Error: "connect ECONNREFUSED"
- Cloud SQL Proxy not running
- Wrong host/port configuration
- Firewall blocking connection

### Error: "Connection terminated unexpectedly"
- Database credentials incorrect
- User doesn't have access to database
- SSL configuration mismatch

### Error: "too many connections"
- Reduce DB_POOL_MAX
- Check for connection leaks
- Review Cloud SQL instance connection limit

### Error: "could not connect to server"
- Check INSTANCE_CONNECTION_NAME format
- Verify Cloud SQL instance is running
- Ensure service account has Cloud SQL Client role

