from urllib.parse import urlparse
import scrapy
from bs4 import BeautifulSoup

class TechGiantsSpider(scrapy.Spider):
    name = "tech_giants"
    
    allowed_domains = [
        "about.meta.com",
        "aws.amazon.com",
        "en.wikipedia.org"  
    ]

    start_urls = [
        "https://about.meta.com/news",
        "https://aws.amazon.com/blogs",
        "https://en.wikipedia.org/wiki/Category:Technology_companies_of_the_United_States" # Added Wikipedia Start
    ]

    def parse(self, response):
        # --- LANGUAGE CHECK ---
        # Get the language attribute from the HTML tag (e.g., <html lang="en">)
        lang = response.css('html::attr(lang)').get()
        # If a language is specified and it does NOT start with 'en', skip this page.
        if lang and not lang.lower().startswith('en'):
            return

        # --- Standard Parsing ---
        title = response.css('title::text').get(default="unknown")
        description = response.css('meta[name="description"]::attr(content)').get(
            default=response.css('meta[property="og:description"]::attr(content)').get(
                default="no description"
            )
        )

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Clean up: remove scripts, styles, and navigation elements
        for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script_or_style.decompose()

        content_text = soup.get_text(separator=" ", strip=True)
        content_text=content_text[:1000]

        # Only yield if there is substantial content
        if len(content_text) > 200:
            yield {
                "url": response.url,
                "domain": urlparse(response.url).netloc,
                "company": urlparse(response.url).netloc.split(".")[-2].split("-")[-1],
                "title": title,
                "description": description,
                "content": content_text,
            }

        article_patterns = [
            '::attr(href)[contains(., "/blog/")]',
            '::attr(href)[contains(., "/post/")]',
            '::attr(href)[contains(., "/news/")]',
            '::attr(href)[contains(., "/article/")]',
            '::attr(href)[contains(., "/wiki/")]', # Pattern for Wikipedia articles
        ]

        for selector in article_patterns:
            for link in response.css(f'a{selector}').getall():
                # Scrapy will automatically filter out domains not in 'allowed_domains'.
                # Since we only allowed 'en.wikipedia.org', links to 'fr.wikipedia.org' are blocked automatically.
                yield response.follow(link, self.parse)