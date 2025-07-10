from django.core.management.base import BaseCommand
from upwork_crawler.upwork_crawler.models import Job
from upwork_crawler.services.gpt_evaluator import evaluate_job_with_gpt

class Command(BaseCommand):
    help = "Evaluate jobs using GPT"

    def handle(self, *args, **kwargs):
        jobs = Job.objects.filter(gpt_response__isnull=True)

        self.stdout.write(f"👉 Found {jobs.count()} jobs to evaluate")

        for job in jobs:
            try:
                result = evaluate_job_with_gpt(job.description)

                if result:
                    job.gpt_difficulty = result["gpt_difficulty"]
                    job.gpt_intern = result["gpt_intern"]
                    job.gpt_copilot = result["gpt_copilot"]
                    job.gpt_estimated_hours = result["gpt_estimated_hours"]
                    job.gpt_response = result["gpt_response"]

                    job.save()
                    self.stdout.write(f"✅ {job.title[:40]}... → scored {job.gpt_difficulty}")
                else:
                    self.stderr.write(f"❌ GPT failed for: {job.title}")
            except Exception as e:
                self.stderr.write(f"[GPT ERROR] {e}")
