#!/bin/bash

export PROJECT_ID=zhmichael-demo
export REGION=us-central1
export IMAGE=us-central1-docker.pkg.dev/zhmichael-demo/gemini-proxy/gemini-proxy:v8

if [ ! $PROJECT_ID ]; then
    echo "please set PROJECT_ID"
    exit 1
fi

if [ ! $REGION ]; then
    echo "please set REGION"
    exit 1
fi

echo "Create service account for gemini proxy ... "
gcloud iam service-accounts create gemini-proxy \
    --description="Service account for gemini proxy" \
    --display-name="gemini-proxy" \
    --project=${PROJECT_ID}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:gemini-proxy@${PROJECT_ID}.iam.gserviceaccount.com \
    --role='roles/aiplatform.user'  \
    --condition=None \
    --quiet > /dev/null

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:gemini-proxy@${PROJECT_ID}.iam.gserviceaccount.com \
    --role='roles/secretmanager.secretAccessor' \
    --condition=None \
    --quiet > /dev/null

echo "Create secret from your config.yaml"
gcloud secrets create gemini-proxy-config \
    --replication-policy="automatic" \
    --data-file="config.yaml"

echo "Deploy gemini proxy on CLoud Run"
gcloud run deploy gemini-proxy-001 --image=${IMAGE} \
    --max-instances=16 \
    --min-instances=0 \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --service-account gemini-proxy@${PROJECT_ID}.iam.gserviceaccount.com \
    --cpu=1 \
    --memory=512Mi \
    --concurrency=4 \
    --port=4000 \
    --allow-unauthenticated \
    --timeout=90 \
    --update-secrets=/config/config.yaml=gemini-proxy-config:latest