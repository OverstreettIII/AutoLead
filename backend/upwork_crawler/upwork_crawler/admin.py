from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Job
from upwork_crawler.services.lead_scorer import calculate_lead_score  # Import hàm tính điểm GPT

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "id", "title", "lead_score", "gpt_difficulty", "is_potential_lead", "is_sent_email",
        "posted_time", "budget_min", "budget_max", "currency",
        "client_country", "client_rating", "client_total_jobs", "client_total_spend"
    ]
    list_filter = ("lead_score", "gpt_difficulty", "is_sent_email", "is_potential_lead", "client_country")
    search_fields = ("title", "description", "url")
    ordering = ("-posted_time",)

    actions = ["send_email_again", "evaluate_gpt"]  # Thêm action mới

    def send_email_again(self, request, queryset):
        for job in queryset:
            try:
                send_mail(
                    subject=f"Job Update: {job.title}",
                    message=f"Details:\n\n{job.description}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_TO],
                )
                job.is_sent_email = True
                job.save()
                self.message_user(request, f"Email đã được gửi lại cho job: {job.title}")
            except Exception as e:
                self.message_user(request, f"Lỗi khi gửi email cho job: {job.title} - {e}", level="error")
    send_email_again.short_description = "Send Email Again"

    def evaluate_gpt(self, request, queryset):
        for job in queryset:
            try:
                # Đánh giá lại GPT
                score = calculate_lead_score(job)  # Tính lại điểm GPT
                job.gpt_difficulty = score  # Cập nhật độ khó GPT
                job.save()
                self.message_user(request, f"Đánh giá lại GPT cho job: {job.title} thành công.")
            except Exception as e:
                self.message_user(request, f"Lỗi khi đánh giá lại GPT cho job: {job.title} - {e}", level="error")
    evaluate_gpt.short_description = "GPT Reevaluate"
