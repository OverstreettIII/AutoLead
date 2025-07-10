import os
import time
import json
from openai import OpenAI
from upwork_crawler.upwork_crawler.models import Job
from dotenv import load_dotenv
load_dotenv(dotenv_path="/app/.env")  # nạp thủ công biến môi trường

client = OpenAI(api_key=os.getenv("OPENAI_API_TOKEN"))

PROMPT_TEMPLATE = """
Yêu cầu job:
{job_description}

Hãy đánh giá:
1. Độ khó task (1-10)
2. Intern Dev có làm được không?
3. Copilot hỗ trợ được không?
4. Ước lượng thời gian hoàn thành (giờ)

⚠️ Trả về đúng định dạng JSON như sau, KHÔNG viết gì ngoài nó:

{{
    "gpt_difficulty": 4,
    "gpt_intern": true,
    "gpt_copilot": true,
    "gpt_estimated_hours": 15.5
}}
"""

def evaluate_job_with_gpt(job_description):
    prompt = PROMPT_TEMPLATE.format(job_description=job_description)

    print("\n📝 Prompt gửi GPT:")
    print(prompt[:1000])

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            content = response.choices[0].message.content.strip()
            print("\n📩 GPT trả về:")
            print(content)

            parsed = json.loads(content)

            return {
                "gpt_difficulty": int(parsed["gpt_difficulty"]),
                "gpt_intern": bool(parsed["gpt_intern"]),
                "gpt_copilot": bool(parsed["gpt_copilot"]),
                "gpt_estimated_hours": float(parsed["gpt_estimated_hours"]),
                "gpt_response": parsed,
            }

        except Exception as e:
            print(f"[GPT ERROR] {type(e).__name__}: {e}")
            time.sleep(2)

    return None

def run_gpt_evaluation():
    jobs = Job.objects.filter(gpt_response__isnull=True)
    print(f"👉 Found {jobs.count()} jobs to evaluate")

    for job in jobs:
        print(f"\n✨ Evaluating job: {job.title}")

        try:
            result = evaluate_job_with_gpt(job.description)

            if result:
                job.gpt_difficulty = result["gpt_difficulty"]
                job.gpt_intern = result["gpt_intern"]
                job.gpt_copilot = result["gpt_copilot"]
                job.gpt_estimated_hours = result["gpt_estimated_hours"]
                job.gpt_response = result["gpt_response"]
                job.save()
                print(f"✅ Saved GPT evaluation for: {job.title}")
            else:
                print(f"❌ GPT evaluation failed (no result) for: {job.title}")

        except Exception as e:
            print(f"❌ GPT evaluation ERROR for: {job.title}")
            print(f"[ERROR] {type(e).__name__}: {e}")
