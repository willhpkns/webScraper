import scrapy
from bs4 import BeautifulSoup
import re
from bs4.element import Comment

class StudycentralauSpider(scrapy.Spider):
    name = "studycentralau"
    allowed_domains = ["studycentralau.com"]
    start_urls = ["https://studycentralau.com"]

    def parse(self, response):
        page_data = self.parse_web_page(response.text)  # Use response.text instead of response.body
        yield page_data

    def parse_web_page(self, body, contentSelector=None, removeSelector=None):
        contentSelector = contentSelector or []
        removeSelector = removeSelector or []

        soup = BeautifulSoup(body, 'html.parser')
        title = soup.head.title.string if soup.head and soup.head.title else soup.title.string if soup.title else ''
        
        for selector in ['head', 'header:nth-child(1)', 'menu', 'nav', 'footer:nth-last-child(1)', 'meta', 'script', 'link', 'style', 'noscript', 'svg', 'input'] + removeSelector:
            for tag in soup.select(selector):
                tag.extract()

        for tag in soup.find_all(True):
            tag.unwrap()  # Remove tags, keep text content

        # Removing comments
        for element in soup(text=lambda text: isinstance(text, Comment)):
            element.extract()

        # Extracting text and cleaning up
        text_content = soup.get_text(separator=' ', strip=True)
        text_content = re.sub(r'<[^>]+>', ' ', text_content)  # Remove any leftover HTML tags
        text_content = re.sub(r'\s+', ' ', text_content)  # Remove sequences of whitespace
        text_content = re.sub(r'[^\w\s]', '', text_content)  # Remove non-linguistic symbols
        
        # Sentence segmentation
        sentences = re.split(r'(?<=[.!?]) +', text_content)

        return {
            'html': soup.prettify(),
            'title': title,
            'content': sentences
        }
