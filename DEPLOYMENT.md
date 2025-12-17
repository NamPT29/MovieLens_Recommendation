# Cloud Deployment Guide

## Azure App Service Deployment

### Prerequisites

```bash
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login
az login
```

### Deploy to Azure

```bash
# Create resource group
az group create --name movielens-rg --location eastus

# Create App Service plan
az appservice plan create \
    --name movielens-plan \
    --resource-group movielens-rg \
    --sku B1 \
    --is-linux

# Create web app
az webapp create \
    --resource-group movielens-rg \
    --plan movielens-plan \
    --name movielens-recommender \
    --runtime "PYTHON:3.12" \
    --deployment-container-image-name movielens-recommender:latest

# Configure app settings
az webapp config appsettings set \
    --resource-group movielens-rg \
    --name movielens-recommender \
    --settings \
        WEBSITE_PORT=8501 \
        SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

## Docker Deployment (Local/Cloud)

### Build and Run Locally

```bash
# Build image
docker build -t movielens-recommender .

# Run container
docker run -p 8501:8501 movielens-recommender

# Or use docker-compose
docker-compose up -d
```

### Push to Azure Container Registry

```bash
# Create ACR
az acr create \
    --resource-group movielens-rg \
    --name movielensacr \
    --sku Basic

# Login to ACR
az acr login --name movielensacr

# Tag and push
docker tag movielens-recommender movielensacr.azurecr.io/movielens-recommender:latest
docker push movielensacr.azurecr.io/movielens-recommender:latest
```

## Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect GitHub repository
4. Deploy with one click
5. Add secrets in dashboard:
   - MYSQL_HOST
   - MYSQL_PASSWORD
   - etc.

## AWS EC2 Deployment

```bash
# SSH to EC2 instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# Clone repo
git clone <your-repo-url>
cd KHDL_cuoiky

# Run with docker-compose
sudo docker-compose up -d
```

## Environment Variables

Create `.env` file:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=recommender
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=movielens
```

## Monitoring

### Application Insights (Azure)

```python
# Add to requirements.txt
# opencensus-ext-azure
# opencensus-ext-flask

# In app.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=<your-key>'
))
```

### Basic Health Check

```python
# Add to app.py
import streamlit as st

@st.cache_data(ttl=60)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True
    }
```
