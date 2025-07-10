from django.db import models

class Job(models.Model):
    # Thông tin cơ bản về job
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.CharField(max_length=50, blank=True, null=True)
    budget_min = models.IntegerField(blank=True, null=True)
    budget_max = models.IntegerField(blank=True, null=True)
    average_bid = models.CharField(max_length=50, blank=True, null=True)
    posted_time = models.CharField(max_length=50)
    tags = models.JSONField(default=list)
    url = models.URLField(unique=True)  # ✅ tránh trùng job

    # Thông tin về client
    client_country = models.CharField(max_length=100, blank=True, null=True)
    client_rating = models.CharField(max_length=10, blank=True, null=True)
    client_total_jobs = models.CharField(max_length=10, blank=True, null=True)
    client_total_spend = models.CharField(max_length=50, blank=True, null=True)

    # Đánh giá từ GPT
    gpt_difficulty = models.IntegerField(blank=True, null=True)
    gpt_intern = models.BooleanField(blank=True, null=True)
    gpt_copilot = models.BooleanField(blank=True, null=True)
    gpt_estimated_hours = models.FloatField(blank=True, null=True)
    gpt_response = models.JSONField(blank=True, null=True)

    # Thông tin hệ thống
    created_at = models.DateTimeField(auto_now_add=True)

    # Các cờ trạng thái dùng cho Module 3 và 4
    lead_score = models.IntegerField(blank=True, null=True)
    is_potential_lead = models.BooleanField(default=False)
    is_sent_email = models.BooleanField(default=False)
    currency = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.title
