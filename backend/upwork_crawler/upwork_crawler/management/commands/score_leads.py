from django.core.management.base import BaseCommand
from upwork_crawler.upwork_crawler.models import Job
from upwork_crawler.services.lead_scorer import calculate_lead_score


class Command(BaseCommand):
    help = "Score leads"

    def handle(self, *args, **kwargs):
        jobs = Job.objects.filter(lead_score__isnull=True)

        self.stdout.write(f"👉 Found {jobs.count()} jobs to score")

        for job in jobs:
            try:
                score = calculate_lead_score(job)
                job.lead_score = score
                job.is_potential_lead = score >= 8  # ✅ Thêm dòng này để đánh dấu job tiềm năng
                job.save()
                self.stdout.write(f"✔️ Job ID {job.id} scored {score}")
            except Exception as e:
                self.stderr.write(f"[ERROR] Job ID {job.id} failed: {e}")
