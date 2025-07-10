from datetime import datetime

def convert_to_usd(amount, currency):
    exchange_rates = {
        "USD": 1,
        "INR": 1 / 83,
        "EUR": 1.1,
        "GBP": 1.3,
        # Add more if needed
    }
    return amount * exchange_rates.get(currency, 0)

def calculate_lead_score(job):
    score = 0

    # Tính điểm dựa trên budget
    if job.budget_min and job.currency:
        budget_usd = convert_to_usd(job.budget_min, job.currency)
        if budget_usd > 200:
            score += 2

    if job.gpt_difficulty is not None and job.gpt_difficulty <= 4:
        score += 2
    if job.gpt_intern:
        score += 3
    if job.gpt_copilot:
        score += 1

    # ✅ Convert rating từ str → float
    try:
        rating = float(job.client_rating)
        if rating > 4.5:
            score += 2
    except:
        pass

    # ✅ Convert total_jobs từ str → int
    try:
        total_jobs = int(job.client_total_jobs)
        if total_jobs > 10:
            score += 2
    except:
        pass

    # ✅ posted_time đã xử lý thành datetime thì mới tính
    if job.posted_time and isinstance(job.posted_time, datetime):
        if (datetime.utcnow() - job.posted_time).total_seconds() < 86400:
            score += 1

    return score
