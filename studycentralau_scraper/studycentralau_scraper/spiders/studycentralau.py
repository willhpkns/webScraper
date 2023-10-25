import scrapy
from bs4 import BeautifulSoup
from bs4.element import Comment



class StudycentralauSpider(scrapy.Spider):
    name = "studycentralau"
    allowed_domains = ["studycentralau.com"]
    start_urls = ["https://studycentralau.com"]

    def parse(self, response):
        page_data = self.parse_web_page(response.body)
        yield page_data

    def parse_web_page(self, body, contentSelector=None, removeSelector=None):
        contentSelector = contentSelector or []
        removeSelector = removeSelector or []

        soup = BeautifulSoup(body, 'html.parser')
        title = soup.head.title.string if soup.head and soup.head.title else soup.title.string if soup.title else ''
        
        selectedElement = next((soup.select(selector) for selector in contentSelector if soup.select(selector)), None)
        
        for selector in ['head', 'header:nth-child(1)', 'menu', 'nav', 'footer:nth-last-child(1)', 'meta', 'script', 'link', 'style', 'noscript', 'svg'] + removeSelector:
            for tag in soup.select(selector):
                tag.extract()
                
        for tag in soup.find_all('input'):
            tag.extract()

        for tag in soup.find_all(True):
            if tag.name not in ['i']:
                tag.attrs = {key: value for key, value in tag.attrs.items() if not key.startswith('data-')}
                del tag['class']
            del tag['id'], tag['style'], tag['width'], tag['height']

        for img_tag in soup.find_all('img'):
            del img_tag['srcset'], img_tag['sizes'], img_tag['loading'], img_tag['decoding']
        
        for tag in soup.find_all(['span', 'p', 'div'], text='', recursive=False):
            tag.extract()

        for element in soup(text=lambda text: isinstance(text, Comment)):
            element.extract()

        content = selectedElement[0].encode_contents().decode('utf-8') if selectedElement else next((tag.encode_contents().decode('utf-8') for tag in soup.select('main, #main')), soup.body.encode_contents().decode('utf-8'))

        return {
            'html': soup.prettify(),
            'title': title,
            'content': content
        }

