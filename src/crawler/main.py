from scrapy import Spider
from wordpress_xmlrpc import Client, WordPressPost

class ContentSpider(Spider):
    name = 'content_spider'
    
    def parse(self, response):
        # Site özel parsing işlemleri
        title = response.css('h1::text').get()
        content = response.css('article::text').get()
        
        # WordPress'e gönder
        self.post_to_wordpress(title, content) 