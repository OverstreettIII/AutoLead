from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import os

# ✅ Cho phép Django và Scrapy nhận diện đúng module
sys.path.append("/app")
sys.path.append("/app/upwork_crawler")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autolead_django.settings")
import django
django.setup()

# ✅ Import đúng path thực tế
from upwork_crawler.upwork_crawler.spiders.freelancer_spider import FreelancerSpider


class Command(BaseCommand):
    help = "Crawl jobs từ Freelancer"

    def handle(self, *args, **kwargs):
        self.stdout.write("👉 📡 Crawl jobs")
        process = CrawlerProcess(get_project_settings())
        process.crawl(FreelancerSpider)
        process.start()
