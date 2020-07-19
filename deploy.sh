PROJECT_ID='YOUR_PROJECT_ID'
IMAGE_URL="gcr.io/${PROJECT_ID}/covid19-dashboard"
REGION='asia-east1'
PORT='80'

echo "Logging in to Google Cloud...=========================================="
gcloud auth login
echo "Setting project...====================================================="
gcloud config set project ${PROJECT_ID}
echo "Building images...====================================================="
gcloud builds submit --tag ${IMAGE_URL}
echo "Deploying into Cloud Run...============================================"
gcloud run deploy --region=${REGION} --image ${IMAGE_URL} --platform managed --allow-unauthenticated --port=${PORT} --memory=2Gi