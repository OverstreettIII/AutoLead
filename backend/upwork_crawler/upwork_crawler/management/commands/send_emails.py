from django.core.management.base import BaseCommand
from upwork_crawler.upwork_crawler.models import Job


from upwork_crawler.services.email_sender import send_job_email
class Command(BaseCommand):
    help = "Send potential leads via email"

    def handle(self, *args, **kwargs):
        jobs = Job.objects.filter(lead_score__gte=8, is_sent_email=False)

        if not jobs.exists():
            self.stdout.write("❗ No new potential leads to send.")
            return

        self.stdout.write(f"📬 Found {jobs.count()} potential leads to send...")

        for job in jobs:
            try:
                send_job_email(job)
                job.is_sent_email = True
                job.save()
                self.stdout.write(f"✅ Sent email for job ID {job.id}")
            except Exception as e:
                self.stderr.write(f"❌ Failed to send email for job {job.id}: {e}")
