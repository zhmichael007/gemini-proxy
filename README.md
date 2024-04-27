# Vertex AI Gemini Proxy on CloudRun
This repo helps to deploy Vertex AI Gemini proxy on Google Cloud Run with one step. 

**why need proxy?**
- Existing OpenAI users do not need to change the code. They only need to modify the base URL and API Key to access Gemini models.
- Build a proxy to solve the problem of inability to access Google API in China.
- Build a unified Gemini Proxy platform. Various applications can be directly connected using API Key. There is no need to integrate Service Account. 
- Various open source projects already support OpenAI, but do not support the Vertex Gemini model. With this, they will be compatible with all without major modifications.

## Open Cloud Shell
<img width="373" alt="image" src="https://github.com/zhmichael007/gemini-proxy/assets/19321027/f1458da5-158f-4dcd-a4ea-4df402f048b7">

## Git clone the code from Github
```
git clone https://github.com/zhmichael007/gemini-proxy.git
cd gemini-proxy
```

## Prepare your Gemini proxy config yaml file
Edit config.yaml
1. modify "vertex_project" and "vertex_location"
2. Set the temperature, for example: 0.5
3. modify "master_key" as the authentication key in POST

## Build the docker image and push to Artifact Registry
```
export PROJECT_ID=your_project_id
export REGION=region_name
gcloud config set project $PROJECT_ID
```
create repo:
```
gcloud artifacts repositories create gemini-proxy \
   --repository-format=docker \
   --location=${REGION} \
   --description="Docker repository"
```
build the docker image:
```
sudo docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/gemini-proxy/gemini-proxy:v1 .
```
verify if the image is built:
```
docker images
```
push the docker image to AR:
```
sudo gcloud auth configure-docker ${REGION}-docker.pkg.dev
sudo docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/gemini-proxy/gemini-proxy:v1
```
verify if the image is pushed to AR:
<img width="882" alt="image" src="https://github.com/zhmichael007/gemini-proxy/assets/19321027/cdcecc6f-28a1-4cf4-ad71-efb706602c02">

## Deploy Gemini proxy on CloudRun
```
export IMAGE=${REGION}-docker.pkg.dev/${PROJECT_ID}/gemini-proxy/gemini-proxy:v1
bash deploy.sh
```
wait until the deploy finished:
<img width="983" alt="image" src="https://github.com/zhmichael007/gemini-proxy/assets/19321027/2d149217-d40b-4ed0-9c2c-a802349d8669">

## Test
- use curl to test
```
curl --location 'https://gemini-proxy-001-c2574amhxa-df.a.run.app/prompt' \
--header 'Authorization: Bearer sk-1234' \
--header 'Content-Type: application/json' \
--data '{
      "model": "gemini-1.0-pro-001",
      "prompt": "Who are you?"
    }'
```

Result Sample:

<img width="727" alt="image" src="https://github.com/zhmichael007/gemini-proxy/assets/19321027/541f582a-fba9-4605-92e6-112e60627784">

## Update your config.yaml file
1. Upload your new config.yaml to a new secret version
```
gcloud secrets versions add gemini-proxy-config \
    --data-file="config.yaml" \
    --project=${PROJECT_ID}
```
2. Reload the Cloud Run service
```
gcloud run services update gemini-proxy-001 \
    --region=${REGION} \
    --project=${PROJECT_ID} \
    --set-secrets=/config/config.yaml=gemini-proxy-config:latest
```
After update, the endpoint of cloud run keeps the same. 

## Clean
```
export PROJECT_ID=your_project_id
export REGION=region_name
bash clean.sh
```
