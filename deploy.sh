#!/bin/bash
set -e

echo "📦 Preparing environment variables..."
python3 -c '
import sys

env_dict = {}
try:
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env_dict[key] = val

    with open("env.yaml", "w") as f:
        for k, v in env_dict.items():
            v = v.replace("\"", "\\\"")
            f.write(f"{k}: \"{v}\"\n")
except Exception as e:
    print(f"Error parsing .env: {e}")
    sys.exit(1)
'

echo "🚀 Deploying to Google Cloud Run..."
gcloud run deploy finance-bot \
    --source . \
    --region=us-central1 \
    --project=telegrambot-499720 \
    --env-vars-file=env.yaml \
    --quiet

echo "🧹 Cleaning up..."
rm -f env.yaml

echo "✅ Deployment complete!"
