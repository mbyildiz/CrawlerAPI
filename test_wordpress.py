import asyncio
from crawlers.hepsiburada_crawler import HepsiburadaCrawler
from wordpress.publisher import WordPressPublisher
from config.settings import WP_CONFIG
import logging

async def test_wordpress_upload():
    # Test URL
    test_url = "https://www.hepsiburada.com/bosch-25-li-pro-vidalama-seti-2607017037-pm-HB00000WQZEQ"
    
    try:
        # Veriyi çek
        crawler = HepsiburadaCrawler(test_url)
        content = await crawler.crawl()
        
        # WordPress'e gönder
        wp = WordPressPublisher(
            wp_url=WP_CONFIG['url'],
            username=WP_CONFIG['username'],
            password=WP_CONFIG['password']
        )
        
        post_id = wp.publish_post(content, status='draft')
        print(f"\nYazı başarıyla oluşturuldu: {WP_CONFIG['url']}/wp-admin/post.php?post={post_id}&action=edit")
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_wordpress_upload()) 