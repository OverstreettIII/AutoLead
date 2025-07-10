from django.core.management.base import BaseCommand
import subprocess
from datetime import datetime
import sys

class Command(BaseCommand):
    help = "Chạy pipeline: crawl → GPT → scoring → gửi email"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 START PIPELINE")
        start_time = datetime.now()

        steps = [
            ("📡 Crawl jobs", [sys.executable, "manage.py", "crawl_jobs"]),
            ("🤖 Evaluate with GPT", [sys.executable, "manage.py", "evaluate_jobs"]),
            ("🧮 Score leads", [sys.executable, "manage.py", "score_leads"]),
            ("📬 Send emails", [sys.executable, "manage.py", "send_emails"]),
        ]

        for step_name, command in steps:
            self.stdout.write(f"👉 {step_name}")
            try:
                result = subprocess.run(command, capture_output=True, text=True)
                self.stdout.write(result.stdout)
                if result.stderr:
                    self.stderr.write(result.stderr)
            except Exception as e:
                self.stderr.write(f"❌ Error in step: {step_name} → {str(e)}")

        end_time = datetime.now()
        self.stdout.write(f"✅ END PIPELINE. Total time: {end_time - start_time}")
