import scrapy
from urllib.parse import urlparse
from bs4 import BeautifulSoup


class WikipediaTechSpider(scrapy.Spider):
    name = "wiki_tech"

    allowed_domains = ["en.wikipedia.org"]
    start_urls = [
        "https://en.wikipedia.org/wiki/Category:Technology_companies_of_the_United_States",
        "https://en.wikipedia.org/wiki/Category:Software_companies_of_the_United_States",
        "https://en.wikipedia.org/wiki/Category:Artificial_intelligence_companies",
        "https://en.wikipedia.org/wiki/Category:Semiconductor_companies",
        "https://en.wikipedia.org/wiki/Category:Cloud_computing_providers",
        "https://en.wikipedia.org/wiki/Category:Technology_companies_by_country"
    ]

    visited = set()

    TECH_KEYWORDS = [
        "software", "technology", "electronics", "computer",
        "semiconductor", "ai", "artificial intelligence",
        "robotics", "telecommunications", "chips",
        "cloud", "information technology", "machine learning"
    ]

    def parse(self, response):

        links = response.css("#mw-pages a::attr(href)").getall()
        for link in links:
            full = response.urljoin(link)
            if full not in self.visited:
                self.visited.add(full)
                yield scrapy.Request(full, callback=self.parse_company_page)

        subcats = response.css("#mw-subcategories a::attr(href)").getall()
        for link in subcats:
            yield response.follow(link, self.parse)

    def parse_company_page(self, response):

        soup = BeautifulSoup(response.text, "html.parser")

        categories = response.css("#mw-normal-catlinks ul li a::text").getall()
        categories_lower = [c.lower() for c in categories]

        cat_text = " ".join(categories_lower)

        if not any(word in cat_text for word in ["company", "companies", "corporation", "brand", "organization","ai","open-source"]):
            return

        # ✅ STRICTLY REQUIRE THIS TO BE TECH
        if not any(keyword in cat_text for keyword in self.TECH_KEYWORDS):
            return

        title = response.css("h1#firstHeading *::text").get()
        if not title:
            title = soup.find("h1", {"id": "firstHeading"})
            title = title.get_text(strip=True) if title else "unknown"

        summary = ""
        for p in soup.select("div.mw-parser-output > p"):
            text = p.get_text(" ", strip=True)
            if text and not text.startswith("Coordinates"):
                summary = text
                break

        infobox_data = {}
        infobox = soup.select_one("table.infobox")
        if infobox:
            for row in infobox.select("tr"):
                key = row.select_one("th")
                val = row.select_one("td")
                if key and val:
                    k = key.get_text(" ", strip=True)
                    v = val.get_text(" ", strip=True)
                    infobox_data[k] = v

        for tag in soup(["script", "style", "table", "sup"]):
            tag.decompose()

        full_text = soup.get_text(" ", strip=True)
        full_text = full_text.replace(summary, "")
        full_text = full_text[:1500]

        if len(full_text) > 200:

            domain = urlparse(response.url).netloc
            company = title.split("(")[0].strip()

            yield {
                "url": response.url,
                "title": title,
                "description": summary,       # fallback description
                "summary": summary,
                "infobox": infobox_data,
                "categories": categories,
                "content": summary + " " + full_text,
                "domain": domain,
                "company": company,
                "source": "wikipedia"
            }


        for link in response.css('a[href*="/wiki/"]::attr(href)').getall():

            if any([
                link.startswith("/wiki/Special:"),
                link.startswith("/wiki/Talk:"),
                link.startswith("/wiki/Help:"),
                link.startswith("/wiki/File:"),
                ":" in link[6:]
            ]):
                continue

            full_url = response.urljoin(link)

            if full_url not in self.visited:
                self.visited.add(full_url)
                yield scrapy.Request(full_url, callback=self.parse_company_page)
