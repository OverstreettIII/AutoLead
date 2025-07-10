#!/bin/bash

echo "=== 🚀 RUNNING PIPELINE $(date) ==="

cd /app


# ✔️ Kiểm tra có tồn tại file .env không
if [ -f .env ]; then
    echo "🔧 .env found"
else
    echo "❌ .env not found!"
fi

# In ra token length để debug
echo "🔑 OPENAI_API_TOKEN length (from shell): ${#OPENAI_API_TOKEN}"

echo "🚀 Starting: python manage.py run_pipeline"

if /usr/local/bin/python manage.py run_pipeline; then
    echo "✅ PIPELINE ran successfully."
else
    echo "❌ Error occurred during: python manage.py run_pipeline"
fi

echo "=== ✅ PIPELINE FINISHED ==="
