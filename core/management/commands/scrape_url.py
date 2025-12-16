from django.core.management.base import BaseCommand
from core.scraper import scrape_url_summary
from django.utils.text import Truncator
from core.models import OrganizationDoc

class Command(BaseCommand):
    help = 'Scrape a url and create OrganizationDoc (usage: python manage.py scrape_url https://example.com)'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)
        parser.add_argument('--title', type=str, default=None)

    def handle(self, *args, **options):
        url = options['url']
        title = options.get('title')
        self.stdout.write(f"Fetching {url} ...")
        summary = scrape_url_summary(url, max_chars=4000)
        if not summary:
            self.stderr.write("Failed to scrape the URL or no content found.")
            return
        title = title or summary.get('title') or url
        content = summary.get('summary') or ''
        doc = OrganizationDoc.objects.create(
            title=title,
            source_url=url,
            summary=Truncator(content).chars(600),
            content=content,
            scraped=True
        )
        self.stdout.write(self.style.SUCCESS(f"Created doc id={doc.id} title={doc.title}"))
