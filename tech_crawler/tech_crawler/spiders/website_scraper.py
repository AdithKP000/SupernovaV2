# import scrapy
# from urllib.parse import urlparse
# from bs4 import BeautifulSoup
# import re


# class OfficialSitesSpider(scrapy.Spider):
#     name = "official_sites"

#     allowed_domains = [
#         "google.com", "openai.com", "apple.com", "amazon.com",
#         "aws.amazon.com", "microsoft.com", "nvidia.com",
#         "meta.com", "tesla.com"
#     ]

#     start_urls = [
#         "https://www.google.com",
#         "https://openai.com",
#         "https://www.apple.com",
#         "https://www.amazon.com",
#         "https://aws.amazon.com",
#         "https://www.microsoft.com",
#         "https://www.nvidia.com",
#         "https://about.meta.com",
#         "https://www.tesla.com",
#     ]

#     custom_settings = {
#         "DEPTH_LIMIT": 2,
#         "DOWNLOAD_DELAY": 1.0,
#         "ROBOTSTXT_OBEY": True,
#     }

#     # Block language variations
#     non_english_patterns = re.compile(
#         r"/(fr|de|es|it|pt|ar|jp|zh|tr|ru|ko|nl|sv|no|da|pl)/",
#         re.IGNORECASE,
#     )

#     # Block unnecessary or harmful page types
#     banned_patterns = re.compile(
#         r"(support|help|contact|login|signin|signup|cart|checkout|store|buy|purchase|"
#         r"product|pricing|subscribe|careers|jobs|press|terms|privacy|feedback|cookies|"
#         r"faq|billing|payment|account|profile|settings|tracking|advertising|ads|"
#         r"investor|refund|warranty|protection|form|survey)",
#         re.IGNORECASE,
#     )

#     def is_english_text(self, text):
#         english_chars = sum(c.isascii() for c in text)
#         return english_chars / max(len(text), 1) > 0.85

#     def is_useful_page(self, url):
#         return not self.banned_patterns.search(url)

#     def parse(self, response):

#         lang = response.css("html::attr(lang)").get()
#         if lang and not lang.lower().startswith("en"):
#             return

#         if self.non_english_patterns.search(response.url):
#             return

#         if not self.is_useful_page(response.url):
#             return

#         # --------------------------
#         title = response.css("title::text").get(default="unknown").strip()
#         desc = response.css('meta[name="description"]::attr(content)').get(
#             default=response.css('meta[property="og:description"]::attr(content)').get(default="")
#         )

#         soup = BeautifulSoup(response.text, "html.parser")

#         for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
#             tag.decompose()

#         full_text = soup.get_text(separator=" ", strip=True)

#         if not self.is_english_text(full_text):
#             return

#         # Avoid empty or waste content
#         if len(full_text) > 150:
#             yield {
#                 "url": response.url,
#                 "title": title,

#                 "domain": urlparse(response.url).netloc,
#                 "company": urlparse(response.url).netloc.split(".")[0],
                
#                 "description": desc,
#                 "content": full_text[:4000],  # keep moderate size for embeddings
#             }

#         for href in response.css("a::attr(href)").getall():

#             # Skip anchors
#             if href.startswith("#"):
#                 continue

#             # Build absolute URL
#             if href.startswith("/"):
#                 href = response.urljoin(href)

#             parsed = urlparse(href)

#             # Only follow allowed domains
#             if parsed.netloc not in self.allowed_domains:
#                 continue

#             # Block language variations
#             if self.non_english_patterns.search(href):
#                 continue

#             # Block useless customer-care/shop/contact/etc pages
#             if not self.is_useful_page(href):
#                 continue

#             yield scrapy.Request(href, callback=self.parse)






import scrapy
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re


class OfficialSitesSpider(scrapy.Spider):
    name = "official_sites"

    allowed_domains = [
        # "google.com", "openai.com", "apple.com", "amazon.com",
        # "aws.amazon.com", "microsoft.com", "nvidia.com",
        # "meta.com", "tesla.com"
        "anthropic.com",
        "aistudio.google.com",
        "x.ai",
        "paperswithcode.com",
        "deepmind.google",
        "ai.meta.com",
        "runwayml.com",
        "midjourney.com",
        "cohere.com",
        "mistral.ai",
        "perplexity.ai",
        "weightsandbiases.com",
        "elevenlabs.io",
        "together.ai",
           " docs.python.org",
        "nodejs.org",
        "react.dev",
        "nextjs.org",
        "vuejs.org",
        "angular.io",
        "svelte.dev",
        "deno.com",
        "bun.sh",
        "go.dev",
        "rust-lang.org",
        "kotlinlang.org",
        "swift.org",
        "php.net",
        "java.com",
        "spring.io",
        "flask.palletsprojects.com",
        "fastapi.tiangolo.com",
        "django-project.com",
        "pytorch.org",
        "tensorflow.org",
        "numpy.org",
        "pandas.pydata.org",
        "scipy.org",
        "opencv.org",
        "threejs.org",
        "unity.com",
        "unrealengine.com",
        "godotengine.org",
        "electronjs.org",
        "tauri.app",
        "vercel.com",
        "netlify.com",
        "supabase.com"
    ]

    start_urls = [
        # "https://www.google.com",
        # "https://openai.com",
        # "https://www.apple.com",
        # "https://www.amazon.com",
        # "https://aws.amazon.com",
        # "https://www.microsoft.com",
        # "https://www.nvidia.com",
        # "https://about.meta.com",
        # "https://www.tesla.com",
        # "https://anthropic.com",
        # "https://aistudio.google.com",
        # "https://x.ai/",
        # "https://paperswithcode.com",
        # "https://deepmind.google",
        # "https://ai.meta.com",
        # "https://runwayml.com",
        # "https://midjourney.com",
        # "https://cohere.com",
        # "https://mistral.ai",
        # "https://perplexity.ai",
        # "https://weightsandbiases.com",
        # "https://elevenlabs.io",
        # "https://together.ai",
        # "https://pinecone.io",
        # "https://qdrant.tech",
        # "https://weaviate.io",
        # "https://chroma-db.com",
        # "https://ray.io",
        # "https://modal.com",
        # "https://vllm.ai",
        # "https://ollama.ai",
        # "https://kaggle.com",
        # "https://ai.google",
        # "https://fast.ai"
        "https://docs.python.org",
        "https://nodejs.org",
        "https://react.dev",
        "https://nextjs.org",
        "https://vuejs.org",
        "https://angular.io",
        "https://svelte.dev",
        "https://deno.com",
        "https://bun.sh",
            "https://go.dev",
        "https://rust-lang.org",
        "https://kotlinlang.org",
        "https://swift.org",
        "https://php.net",
        "https://java.com",
        "https://spring.io",
        "https://flask.palletsprojects.com",
        "https://fastapi.tiangolo.com",
        "https://django-project.com",
        "https://pytorch.org",
        "https://tensorflow.org",
        "https://numpy.org",
        "https://pandas.pydata.org",
        "https://scipy.org",
        "https://opencv.org",
        "https://threejs.org",
        "https://unity.com",
        "https://unrealengine.com",
        "https://godotengine.org",
        "https://electronjs.org",
        "https://tauri.app",
        "https://vercel.com",
        "https://netlify.com",
        "https://supabase.com"
    ]

    custom_settings = {
        "DEPTH_LIMIT": 2,
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": True,
    }

    # Block language versions
    non_english_patterns = re.compile(
        r"/(fr|de|es|it|pt|ar|jp|zh|tr|ru|ko|nl|sv|no|da|pl)/",
        re.IGNORECASE,
    )

    # Block useless pages
    banned_patterns = re.compile(
        r"(support|docs|changelog|help|contact|login|signin|signup|cart|checkout|store|buy|purchase|"
        r"product|pricing|subscribe|careers|jobs|press|terms|privacy|feedback|cookies|"
        r"faq|billing|payment|account|profile|settings|tracking|advertising|ads|"
        r"investor|refund|warranty|protection|form|survey|doc|documentation|tutorial|example|examples|blog|news|community|" 
        r"forum|forums|api|developer|developers|contribute|contributing|github|gitlab|bitbucket|playground|talks|reference)",
        re.IGNORECASE,
    )

    def is_english_text(self, text):
        english_chars = sum(c.isascii() for c in text)
        return english_chars / max(len(text), 1) > 0.85

    def is_useful_page(self, url):
        return not self.banned_patterns.search(url)

    def parse(self, response):

        lang = response.css("html::attr(lang)").get()
        if lang and not lang.lower().startswith("en"):
            return

        if self.non_english_patterns.search(response.url):
            return

        if not self.is_useful_page(response.url):
            return

        # --------------------------
        title = response.css("title::text").get(default="unknown").strip()
        description = response.css('meta[name="description"]::attr(content)').get(
            default=response.css('meta[property="og:description"]::attr(content)').get(default="")
        )

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
            tag.decompose()

        full_text = soup.get_text(separator=" ", strip=True)

        if not self.is_english_text(full_text):
            return

        if len(full_text) > 150:
            domain = urlparse(response.url).netloc
            company = domain.split(".")[0]

            yield {
                "url": response.url,
                "title": title,
                "description": description,
                "summary": description,           # fallback
                "infobox": {},                    # websites do not have infobox
                "categories": [],                 # not applicable
                "content": full_text[:3000],
                "domain": domain,
                "company": company,
                "source": "official"
            }

        for href in response.css("a::attr(href)").getall():

            if href.startswith("#"):
                continue

            if href.startswith("/"):
                href = response.urljoin(href)

            parsed = urlparse(href)

            if parsed.netloc not in self.allowed_domains:
                continue

            if self.non_english_patterns.search(href):
                continue

            if not self.is_useful_page(href):
                continue

            yield scrapy.Request(href, callback=self.parse)
