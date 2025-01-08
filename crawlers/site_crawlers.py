from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from bs4 import BeautifulSoup

class SiteCrawler:
    def __init__(self, url):
        self.url = url
        self.browser_config = BrowserConfig(
            headless=True,
            verbose=True
        )
        
    async def crawl(self):
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=self.url,
                config=CrawlerRunConfig(
                    cache_mode="ENABLED",
                    word_count_threshold=100  # Minimum kelime sayısı
                )
            )
            
            # İçeriği temizle ve formatla
            soup = BeautifulSoup(result.markdown, 'html.parser')
            
            return {
                'title': soup.find('h1').text if soup.find('h1') else '',
                'content': result.markdown,
                'image_url': self.extract_featured_image(soup),
                'categories': self.extract_categories(soup)
            }
            
    def extract_featured_image(self, soup):
        img = soup.find('img')
        return img.get('src') if img else None
        
    def extract_categories(self, soup):
        # Site özel kategori çıkarma mantığı
        return ['Teknoloji', 'Yapay Zeka']  # Örnek kategoriler 