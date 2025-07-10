import scrapy
import sys
import os
import django
import threading
import re
import logging
from django.db import close_old_connections

# Cho phép Scrapy dùng được Django
sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autolead_django.settings")
django.setup()

from upwork_crawler.upwork_crawler.models import Job

class FreelancerSpider(scrapy.Spider):
    name = "freelancer"
    allowed_domains = ["freelancer.com"]

    def start_requests(self):
        logging.info("Starting requests")
        base_url = "https://www.freelancer.com/jobs/{}?keyword=php%2C%20laravel%2C%20wordpress%2C%20python"
        for page in range(1, 7):
            logging.info(f"Fetching page {page}")
            yield scrapy.Request(
                url=base_url.format("" if page == 1 else page),
                callback=self.parse
            )

    def parse(self, response):
        logging.info("Parsing response")
        job_cards = response.css("div.JobSearchCard-item")
        logging.info(f"Found {len(job_cards)} job cards")

        for job in job_cards:
            posted_time = job.css("span.JobSearchCard-primary-heading-days::text").get(default='').strip()
            logging.info(f"Job posted time: {posted_time}")
            if posted_time in ["5 days left", "6 days left", "7 days left", "9 days left"]:
                job_url = response.urljoin(job.css("a.JobSearchCard-primary-heading-link::attr(href)").get())
                logging.info(f"Job URL: {job_url}")
                yield scrapy.Request(
                    url=job_url,
                    callback=self.parse_detail,
                    meta={
                        'title': job.css("a.JobSearchCard-primary-heading-link::text").get(default='').strip(),
                        'url': job_url,
                        'description': job.css("p.JobSearchCard-primary-description::text").get(default='').strip(),
                        'tags': job.css("div.JobSearchCard-primary-tags a::text").getall(),
                        'budget': job.css("div.JobSearchCard-primary-price::text").get(default='').strip(),
                        'average_bid': job.css("span.JobSearchCard-primary-avgBid::text").get(default='').strip(),
                        'posted_time': posted_time,
                    }
                )

    def parse_detail(self, response):
        logging.info("Parsing job details")
        data = response.meta

        # Lấy full description từ thẻ <fl-text>
        description = response.css('fl-text.Project-description div.NativeElement::text').getall()
        data['description'] = ' '.join(description).strip()  # Ghép các đoạn text lại thành một chuỗi

        # Lấy quốc gia client nếu không có từ lần crawl ngoài
        data['client_country'] = response.css("img.FlagImage::attr(title)").get(default='').strip()

        # Lấy rating client nếu không có từ lần crawl ngoài
        data['client_rating'] = response.css("div.RatingContainer .ValueBlock::text").get(default='').strip()

        # Lấy số job đã đăng nếu không có từ lần crawl ngoài
        data['client_total_jobs'] = response.css("fl-review-count div.NativeElement::text").re_first(r'\d+')

        # Lấy tổng số tiền đã chi nếu không có từ lần crawl ngoài
        data['client_total_spend'] = response.xpath(
            "//*[contains(text(), 'spent')]/text()"
        ).re_first(r'\$\d+(?:,\d+)?')

        # Parse budget_min, budget_max và currency từ dòng h2
        budget_text = response.css('div[data-hide-mobile="true"] h2::text').get(default='').strip()

        # Ví dụ: "€8-30 EUR" hoặc "$300-500 USD" hoặc "₹6000-15000 INR"
        match = re.search(r'([₹$€£])\s*([\d,]+)-([\d,]+)', budget_text)
        if match:
            symbol = match.group(1)
            min_budget = int(match.group(2).replace(',', ''))
            max_budget = int(match.group(3).replace(',', ''))

            # Mapping ký hiệu sang mã tiền tệ chuẩn
            currency_map = {
                "$": "USD",
                "₹": "INR",
                "€": "EUR",
                "£": "GBP"
            }
            data['budget_min'] = min_budget
            data['budget_max'] = max_budget
            data['currency'] = currency_map.get(symbol, None)
        else:
            data['budget_min'] = None
            data['budget_max'] = None
            data['currency'] = None

        threading.Thread(target=self.save_job, args=(data,)).start()

    def save_job(self, data):
        logging.info(f"Saving job: {data['url']}")
        try:
            close_old_connections()
            if Job.objects.filter(url=data['url']).exists():
                logging.info("Job already exists")
                return
            Job.objects.create(
                title=data['title'],
                description=data['description'],
                budget_min=data['budget_min'],
                budget_max=data['budget_max'],
                currency=data['currency'],
                url=data['url'],
                client_country=data['client_country'],
                client_rating=float(data['client_rating']) if data['client_rating'] else None,
                client_total_jobs=int(data['client_total_jobs']) if data['client_total_jobs'] else None,
                client_total_spend=float(data['client_total_spend'].replace('$', '').replace(',', '')) if data['client_total_spend'] else None,
                posted_time=data['posted_time']
            )
            self.logger.info(f"✅ Lưu job mới: {data['url']}")
        except Exception as e:
            self.logger.error(f"❌ Lỗi khi lưu job {data['url']}: {e}")
