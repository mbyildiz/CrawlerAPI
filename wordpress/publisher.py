from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import media
from wordpress_xmlrpc.compat import xmlrpc_client
import requests
import os
import logging
from datetime import datetime

class WordPressPublisher:
    def __init__(self, wp_url, username, password):
        self.client = Client(f'{wp_url}/xmlrpc.php', username, password)
        self.image_folder = 'downloaded_images'
        
        # İndirilen resimler için klasör oluştur
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)
    
    def publish_post(self, content, status='draft'):
        """Ürünü WordPress'e gönder"""
        try:
            post = WordPressPost()
            
            # Başlık ve içerik
            post.title = content['title']
            
            # HTML formatında içerik oluştur
            html_content = f"""
                <div class="product-content">
                    <div class="product-price">
                        <strong>Fiyat:</strong> {content['price']}
                    </div>
                    
                    <div class="product-description">
                        <h2>Ürün Açıklaması</h2>
                        {content['description']}
                    </div>
                    
                    <div class="product-gallery">
                        {self._create_image_gallery(content['image_url'], content.get('additional_images', []))}
                    </div>
                </div>
            """
            
            post.content = html_content
            
            # Kategoriler
            if content.get('categories'):
                post.terms_names = {
                    'category': content['categories']
                }
            
            # Durum (draft veya publish)
            post.post_status = status
            
            # Öne çıkan görsel
            if content['image_url']:
                thumbnail_id = self._upload_image(content['image_url'])
                if thumbnail_id:
                    post.thumbnail = thumbnail_id
            
            # Yazıyı yayınla
            post_id = self.client.call(NewPost(post))
            logging.info(f"Yazı başarıyla yayınlandı. ID: {post_id}")
            
            return post_id
            
        except Exception as e:
            logging.error(f"WordPress'e gönderirken hata: {str(e)}")
            raise
    
    def _create_image_gallery(self, main_image, additional_images):
        """Resim galerisi HTML'i oluştur"""
        gallery_html = '<div class="product-images">'
        
        # Ana resim
        if main_image:
            gallery_html += f'<div class="main-image"><img src="{main_image}" alt="Ürün Görseli"></div>'
        
        # Diğer resimler
        if additional_images:
            gallery_html += '<div class="additional-images">'
            for img in additional_images:
                gallery_html += f'<div class="image-item"><img src="{img}" alt="Ürün Detay"></div>'
            gallery_html += '</div>'
        
        gallery_html += '</div>'
        return gallery_html
    
    def _upload_image(self, image_url):
        """Resmi WordPress'e yükle"""
        try:
            # Resmi indir
            response = requests.get(image_url)
            if response.status_code != 200:
                raise Exception(f"Resim indirilemedi: {image_url}")
            
            # Dosya adını oluştur
            filename = f"product_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(self.image_folder, filename)
            
            # Resmi kaydet
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # WordPress'e yükle
            with open(filepath, 'rb') as f:
                data = {
                    'name': filename,
                    'type': 'image/jpeg',
                    'bits': xmlrpc_client.Binary(f.read())
                }
            
            response = self.client.call(media.UploadFile(data))
            logging.info(f"Resim yüklendi: {filename}")
            
            # Geçici dosyayı sil
            os.remove(filepath)
            
            return response['id']
            
        except Exception as e:
            logging.error(f"Resim yüklenirken hata: {str(e)}")
            return None 