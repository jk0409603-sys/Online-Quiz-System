#!/usr/bin/env bash
set -euo pipefail

RESOURCE_GROUP="quiz-rg"
LOCATION="eastus"
PLAN="quiz-plan"
APP_NAME="quiz-system-${RANDOM}"

az group create --name "$RESOURCE_GROUP" --location "$LOCATION"
az appservice plan create --name "$PLAN" --resource-group "$RESOURCE_GROUP" --is-linux --sku B1 --tier Basic
az webapp create --resource-group "$RESOURCE_GROUP" --plan "$PLAN" --name "$APP_NAME" --runtime "PYTHON|3.12"

az webapp config appsettings set --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --settings \
  AZURE_OPENAI_ENDPOINT="${AZURE_OPENAI_ENDPOINT:-}" \
  AZURE_OPENAI_KEY="${AZURE_OPENAI_KEY:-}" \
  AZURE_OPENAI_DEPLOYMENT="${AZURE_OPENAI_DEPLOYMENT:-gpt-4o-mini}" \
  AZURE_LANGUAGE_ENDPOINT="${AZURE_LANGUAGE_ENDPOINT:-}" \
  AZURE_LANGUAGE_KEY="${AZURE_LANGUAGE_KEY:-}"

zip -r app.zip . -x '*.git*' 'quiz_app/*' 'users.txt' 'results.txt'
az webapp deploy --resource-group "$RESOURCE_GROUP" --name "$APP_NAME" --src-path app.zip --type zip

echo "Deployment complete: https://$APP_NAME.azurewebsites.net"
