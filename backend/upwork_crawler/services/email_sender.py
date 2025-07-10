from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from upwork_crawler.upwork_crawler.models import Job


def send_job_email(job):
    clean_title = job.title.strip().replace('\n', ' ')
    subject = f"🔥 New Potential Job Lead: {clean_title}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.EMAIL_TO]

    html_content = render_to_string('email/job_notification.html', {'job': job})
    text_content = f"{clean_title}\n\n{job.description.strip()}\n\nLink: {job.url}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        print(f"✅ Email sent for job {job.id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email for job {job.id}: {e}")
        return False



def process_pending_jobs_for_email():
    """
    Tìm các job tiềm năng chưa gửi, gửi email và cập nhật is_sent_email = True
    """
    jobs = Job.objects.filter(is_potential_lead=True, is_sent_email=False)

    print(f"📬 Found {jobs.count()} potential leads to send...")

    for job in jobs:
        success = send_job_email(job)
        if success:
            job.is_sent_email = True
            job.save()
