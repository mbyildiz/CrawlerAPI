import asyncio
from crawlers.site_crawlers import SiteCrawler
from wordpress.publisher import WordPressPublisher
from config.settings import WP_CONFIG
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)

async def main():
    logging.info("Crawler başlatılıyor...")
    # Crawl edilecek sitelerin listesi
    sites = [
        "https://site1.com/article1",
        "https://site2.com/article2",
        "https://site3.com/article3"
    ]
    
    # WordPress bağlantısını oluştur
    wp = WordPressPublisher(
        wp_url=WP_CONFIG['url'],
        username=WP_CONFIG['username'],
        password=WP_CONFIG['password']
    )
    
    for site in sites:
        try:
            # Siteyi crawl et
            crawler = SiteCrawler(site)
            content = await crawler.crawl()
            
            # WordPress'e gönder
            post_id = wp.publish_post(
                title=content['title'],
                content=content['content'],
                image_url=content['image_url'],
                categories=content['categories']
            )
            
            print(f"Başarıyla yayınlandı: {content['title']} (ID: {post_id})")
            
        except Exception as e:
            print(f"Hata oluştu ({site}): {str(e)}")
            continue

if __name__ == "__main__":
    asyncio.run(main()) 