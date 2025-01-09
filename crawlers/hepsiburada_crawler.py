from bs4 import BeautifulSoup
import logging
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

class HepsiburadaCrawler:
    def __init__(self, url):
        self.url = url
        self.setup_driver()
        
    def setup_driver(self):
        """Selenium WebDriver'ı yapılandır"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Başsız mod
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # WebDriver'ı başlat
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # JavaScript'i devre dışı bırakma özelliğini kapat
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
    def crawl(self):
        logging.info(f"Hepsiburada crawler başlatılıyor: {self.url}")
        
        try:
            # Sayfayı yükle
            self.driver.get(self.url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(5)
            
            # Scroll işlemi - sayfanın tamamını yüklemek için birkaç kez scroll yapalım
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # En başa dön
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Ürün detayları sekmesine tıkla (varsa)
            try:
                # Önce Description ID'li elementi bulmayı dene
                description_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "Description"))
                )
                if not description_element.is_displayed():
                    # Detay sekmesini bul ve tıkla
                    detail_tab = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-test-id="product-detail-tab"]'))
                    )
                    detail_tab.click()
                    time.sleep(3)
            except Exception as e:
                logging.warning(f"Detay sekmesi işlemleri sırasında hata: {str(e)}")
            
            # Sayfanın HTML içeriğini al
            html_content = self.driver.page_source
            
            # HTML içeriğini parse et
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Debug için HTML'i kaydet
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            # Hepsiburada'ya özel selektörler
            title = self.extract_title(soup)
            brand = self.extract_brand(soup)
            price = self.extract_price(soup)
            description, img_descriptions, description_table = self.extract_description(soup)
            images = self.extract_images(soup)
            specs = self.extract_specifications(soup)
            
            logging.info(f"Başlık: {title}")
            logging.info(f"Marka: {brand}")
            logging.info(f"Fiyat: {price}")
            logging.info(f"Açıklama uzunluğu: {len(description)}")
            logging.info(f"Resim sayısı: {len(images)}")
            
            return {
                'title': title,
                'brand': brand,
                'description': description,
                'image_url': images[0] if images else None,
                'additional_images': images[1:],
                'price': price,
                'categories': self.extract_categories(soup),
                'img_description': img_descriptions,
                'description_table': description_table
            }
            
        except Exception as e:
            logging.error(f"Veri çekilirken hata: {str(e)}")
            # Hata durumunda ekran görüntüsü al
            try:
                self.driver.save_screenshot("error_screenshot.png")
            except:
                pass
            raise
        finally:
            # WebDriver'ı kapat
            self.driver.quit()

    def extract_title(self, soup):
        selectors = [
            'h1[data-test-id="title"]',  # Yeni eklenen ana seçici
            'h1.product-name',
            'h1[data-test-id="product-name"]',
            '.product-detail-main h1'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.text.strip()
                logging.debug(f"Başlık bulundu ({selector}): {title}")
                return title
        logging.warning("Başlık bulunamadı!")
        return ''

    def extract_brand(self, soup):
        """Ürünün marka bilgisini çeker"""
        selectors = [
            'a[data-test-id="brand"]',
            'span[data-test-id="brand"]',
            '.brand-name'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                brand = element.text.strip()
                logging.debug(f"Marka bulundu ({selector}): {brand}")
                return brand
        logging.warning("Marka bulunamadı!")
        return ''

    def extract_price(self, soup):
        selectors = [
            'span[data-test-id="price-current-price"]',
            '[data-test-id="price-current-price"]',
            '.price-wrapper span[content]'
        ]
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                price = element.text.strip()
                logging.debug(f"Fiyat bulundu ({selector}): {price}")
                return price
        logging.warning("Fiyat bulunamadı!")
        return ''

    def extract_description(self, soup):
        description_parts = []
        img_descriptions = []
        description_table = {}
        
        def sort_by_length_desc(text_list):
            """Metinleri uzunluklarına göre azalan şekilde sıralar"""
            return sorted(text_list, key=len, reverse=True)
        
        # İstenen içerikler listesi - Uzundan kısaya doğru sıralı
        wanted_texts = sort_by_length_desc([
            "Akü Sayısı",
            "Testere Bıçağı Çapı",
            "Maksimum Tork",
            "Tork Ayarı",
            "Türü",
            "Volt",
            "Akü",
            "Amper",
            "Ahşap Delme Çapı",
            "Çelik Delme Çapı",
            "Delme Derinliği",
            "Delme Çapı",
            "Güç (W)",
            "Darbe Gücü (Joule)",
            "Boşta Maksimum Devir Sayısı (Devir/dk)",
            "Ağırlık",
            "Maksimum Darbe Sayısı (Darbe/dk)",
            "Metal Delme Çapı",
            "Beton Delme Çapı",
            "Akü Bilgisi",
            "Çalışma Şekli",
            "Çalışma Süresi",
            "Çalışma Sıcaklığı",
            "Çalışma Basıncı",
            "Çalışma Hızı",
            "Renk",
            "Uygulama Yüzeyi",
            "Toz Emme",
            "Hız Ayarı",
            "Çanta",
            "Taşıma Kapasitesi",
            "Katlanabilir",
            "Malzeme",
            "Teker Tipi",
            "Disk Çapı",
            "Devir Ayarı",
            "Watt Değeri",
            "Devir",
            "Aksesuar Seti",
            "Aksesuar",
            "Ahşap Kesme (mm)",
            "Metal Kesme (mm)",
            "Türü",
            "Kaldıraç",
            "Kaldırma Kapasitesi",
            "Elektrot Çapı",
            "Çapı",
            "Maksimum Güç (kVA)",
            "Minimum Akım Değeri",
            "Ağırlık (kg)",
            "Ürün Çeşiti",
            "Güvenlik Standardı",
            "Malzeme",
            "Dış Taban",
            "WRU",
            "Su Geçirmez",
            "Koruma Sınıfı",
            "Materyal",
            "EN Standartı",
            "Astar malzemesi",
            "Kaplama malzemesi",
            "Mandren Tipi",
            "Mandren Ölçüsü (mm)",
            "Mandren Çapı (mm)",
            "Mandren Uzunluğu (mm)",
            "Miktar"
        ])
        
        # İstenmeyen içerikler listesi
        unwanted_texts = sort_by_length_desc([
            "Garanti Süresi (Ay)",
            "Yurt Dışı Satış",
            "Stok Kodu",
            "Stok Adedi",
            "Seçenek",
            "Diğer",
            "Kombin ID",
            "Hatalı içerik bildir",
            "Taksit",
            "Stok",
            "Kargo",
            "Teslimat",
            "İade",
            "Satıcı",
            "Mağaza",
            "Kampanya",
            "Hediye",
            "Puan"
        ])
        
        # Ürün açıklaması için selektörler
        selectors = [
            'div#Description',
            'div[id="Description"]',
            'div#product-Description',
            'div[data-test-id="product-detail-description"]',
            'div[data-test-id="product-specs"]',
            'div[id="productDescriptionContent"]',
            'div[id="product-detail-description"]',
            'div.product-information-content',
            'div.product-description-wrapper',
            '.product-information div[data-test-id="product-information-wrapper"]',
            '.product-information-content p'
        ]
        
        time.sleep(3)
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                # Resimleri ayıkla
                images = element.find_all('img')
                for img in images:
                    src = img.get('src')
                    if src and not src.startswith('data:') and ('hepsiburada.net' in src or 'hepsiburada.com' in src):
                        img_descriptions.append(src)
                
                # İstenen içerikleri description_table'a ekle ve description'dan kaldır
                for div in element.find_all('div'):
                    text_content = div.get_text(strip=True)
                    
                    # İstenen içerikleri kontrol et - tam eşleşme ara
                    for wanted in wanted_texts:
                        # Tam eşleşme kontrolü yap
                        if text_content == wanted or text_content.strip(':') == wanted:
                            next_div = div.find_next_sibling('div')
                            if next_div:
                                value = next_div.get_text(strip=True)
                                description_table[wanted] = value
                                next_div.decompose()
                            div.decompose()
                            break
                    
                    # İstenmeyen içerikleri kaldır
                    if any(unwanted in text_content for unwanted in unwanted_texts):
                        next_div = div.find_next_sibling('div')
                        if next_div:
                            next_div.decompose()
                        div.decompose()
                
                text = element.get_text(separator='\n', strip=True)
                if text:
                    description_parts.append(text)
                    logging.debug(f"Açıklama parçası bulundu ({selector}): {text[:100]}...")
        
        # Selenium ile direkt almayı dene
        if not description_parts:
            try:
                description_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Description"))
                )
                if description_element:
                    # Resimleri ayıkla
                    images = description_element.find_elements(By.TAG_NAME, "img")
                    for img in images:
                        src = img.get_attribute('src')
                        if src and not src.startswith('data:') and ('hepsiburada.net' in src or 'hepsiburada.com' in src):
                            img_descriptions.append(src)
                    
                    text = description_element.get_attribute('innerText')
                    if text:
                        # İstenmeyen ve istenen içerikleri metin bazlı temizle
                        cleaned_text = text
                        
                        # İstenen içerikleri description_table'a ekle ve metinden kaldır
                        for wanted in wanted_texts:
                            if wanted in cleaned_text:
                                lines = cleaned_text.split('\n')
                                for i, line in enumerate(lines):
                                    # Tam eşleşme kontrolü yap
                                    if line.strip() == wanted or line.strip(':') == wanted:
                                        if i < len(lines) - 1:
                                            description_table[wanted] = lines[i + 1].strip()
                                            lines[i] = ''
                                            lines[i + 1] = ''
                                cleaned_text = '\n'.join(filter(None, lines))
                        
                        # İstenmeyen içerikleri temizle
                        for unwanted in unwanted_texts:
                            if unwanted in cleaned_text:
                                parts = cleaned_text.split('\n')
                                for i, part in enumerate(parts):
                                    if unwanted in part and i < len(parts) - 1:
                                        parts[i] = ''
                                        parts[i + 1] = ''
                                cleaned_text = '\n'.join(filter(None, parts))
                    
                    description_parts.append(cleaned_text)
                    logging.debug(f"Selenium ile Description ID'den açıklama bulundu: {cleaned_text[:100]}...")
            except Exception as e:
                logging.warning(f"Description ID'den açıklama alınırken hata: {str(e)}")
        
        description = '\n\n'.join(filter(None, description_parts))
        
        # İstenmeyen kelimeleri ve ifadeleri temizle - Uzundan kısaya sıralı
        unwanted_phrases = sort_by_length_desc([
            "Satın aldığınız ürünün orijinal olduğunu gösteren",
            "Satın aldığınız ürünün orijinal olduğunu",
            "Satın aldığınız ürünün",
            "Ürünün orijinal olduğunu gösteren",
            "Ürünün orijinal olduğunu",
            "Ürün özellikleri",
            "Ürünün",
            "Ürünlerimiz",
            "Ürünümüz",
            "Ürünler",
            "Ürün",
            "Fiyat",
            "Fiyatı",
            "Fiyatlar",
            "Kampanya",
            "Kampanyalı",
            "İndirim",
            "İndirimli",
            "Stok",
            "Stokta",
            "Stoklarımızda",
            "Kargo",
            "Kargoya",
            "Kargoyla",
            "Teslimat",
            "Teslim",
            "Taksit",
            "Taksitli",
            "Garanti",
            "Garantili",
            "Orijinal",
            "Orjinal",
            "Mağaza",
            "Mağazamız",
            "Satıcı",
            "Satış",
            "Satışta",
            "Hediye",
            "Hediyeli",
            "Puan",
            "Puanlı",
            "Hatalı içerik bildir"
        ])
        
        # Her bir istenmeyen ifadeyi tam eşleşme ile temizle
        for phrase in unwanted_phrases:
            # Regex pattern oluştur: tam eşleşme için phrase'i escape et
            pattern = re.escape(phrase)
            # Önce ve sonrasında boşluk, noktalama işareti veya satır sonu olabilir
            pattern = f'(?:^|[\\s.,;!?]){pattern}(?:[\\s.,;!?]|$)'
            description = re.sub(pattern, ' ', description, flags=re.IGNORECASE | re.MULTILINE)
        
        # Fazladan boşlukları ve satır sonlarını temizle
        description = '\n'.join(line.strip() for line in description.split('\n') if line.strip())
        
        # Ardışık boş satırları tek satıra indir
        description = re.sub(r'\n\s*\n', '\n', description)
        
        # Fazladan boşlukları temizle
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()
        
        if not description:
            logging.warning("Hiçbir açıklama bulunamadı!")
            # Debug için HTML'i kaydet
            with open('debug_description.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            # Sayfanın ekran görüntüsünü al
            try:
                self.driver.save_screenshot("debug_screenshot.png")
            except Exception as e:
                logging.error(f"Ekran görüntüsü alınırken hata: {str(e)}")
                
        return description, list(set(img_descriptions)), description_table

    def extract_images(self, soup):
        images = set()
        
        # Carousel slide'larını kontrol et
        slide_index = 0
        while True:
            slide_selector = f'[id="pdp-carousel__slide{slide_index}"] img'
            slide_images = soup.select(slide_selector)
            
            if not slide_images:
                break
                
            for img in slide_images:
                src = img.get('src') or img.get('data-src')
                if src and 'http' in src and not src.startswith('data:'):
                    src = src.split('?')[0]
                    if '_org_zoom' not in src:
                        src = src.replace('_small', '_org_zoom')
                    images.add(src)
                    logging.debug(f"Carousel resmi bulundu (slide {slide_index}): {src}")
            
            slide_index += 1
        
        # Eğer carousel'dan resim bulunamazsa, diğer selektörleri dene
        if not images:
            selectors = [
                '[data-test-id="product-image"] img[src]',
                '[data-test-id="carousel-image"] img[src]',
                '[data-test-id="product-gallery"] img[src]',
                'img[src*="productimages.hepsiburada.net"]'
            ]
            
            for selector in selectors:
                for img in soup.select(selector):
                    src = img.get('src') or img.get('data-src')
                    if src and 'http' in src and not src.startswith('data:'):
                        src = src.split('?')[0]
                        if '_org_zoom' not in src:
                            src = src.replace('_small', '_org_zoom')
                        images.add(src)
                        logging.debug(f"Resim bulundu ({selector}): {src}")
        
        if not images:
            logging.warning("Hiç resim bulunamadı!")
            all_images = soup.find_all('img')
            logging.debug(f"Sayfadaki tüm resimler ({len(all_images)}):")
            for img in all_images[:5]:
                logging.debug(f"Image tag: {str(img)}")
        
        image_list = list(images)
        return image_list

    def extract_categories(self, soup):
        try:
            categories = {'main_category': 'Elektronik', 'sub_category': ''}
            
            # Son breadcrumb öğesini bul
            last_breadcrumb = soup.find('span', {'data-test-id': 'breadcrumb-last-item'})
            if last_breadcrumb:
                # Alt kategoriyi kaydet
                categories['sub_category'] = last_breadcrumb.text.strip()
                
                # Son breadcrumb'ın li etiketini bul
                last_li = last_breadcrumb.find_parent('li')
                if last_li:
                    # Bir önceki li etiketini bul
                    prev_li = last_li.find_previous_sibling('li')
                    if prev_li:
                        # Ana kategoriyi al
                        category = prev_li.find('span')
                        if category:
                            categories['main_category'] = category.text.strip()
            
            if not categories['main_category'] and not categories['sub_category']:
                logging.warning("Hiçbir kategori bulunamadı, varsayılan kategoriler döndürülüyor.")
            
            return categories
            
        except Exception as e:
            logging.error(f"Kategori çekilirken hata oluştu: {str(e)}")
            return {'main_category': 'Elektronik', 'sub_category': ''}

    def extract_specifications(self, soup):
        specs = []
        spec_table = soup.select('.data-list tr')
        if spec_table:
            for row in spec_table:
                cols = row.select('td')
                if len(cols) == 2:
                    specs.append(f"{cols[0].text.strip()}: {cols[1].text.strip()}")
        return '\n'.join(specs)