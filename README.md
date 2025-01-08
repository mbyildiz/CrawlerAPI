# Hepsiburada Crawler

Bu proje, Hepsiburada'dan ürün bilgilerini çeken bir web crawler uygulamasıdır. Selenium ve Python kullanılarak geliştirilmiştir.

## Özellikler

- Ürün başlığı, fiyatı ve açıklamasını çekme
- Ürün resimlerini toplama
- Headless Chrome browser kullanımı
- Log sistemi ile hata takibi

## Gereksinimler

- Python 3.x
- Selenium
- Chrome WebDriver
- BeautifulSoup4

## Kurulum

1. Python'u yükleyin (Python 3.x):
   - [Python'un resmi sitesinden](https://www.python.org/downloads/) Python 3.x'i indirin ve yükleyin
   - Yükleme sırasında "Add Python to PATH" seçeneğini işaretleyin

2. Projeyi klonlayın:
   ```bash
   git clone https://github.com/mbyildiz/CrawlerAPI.git
   cd CrawlerAPI
   ```

3. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. Gerekli paketleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

5. Chrome WebDriver'ı yükleyin:
   - [Chrome WebDriver'ı indirin](https://sites.google.com/chromium.org/driver/)
   - İndirilen WebDriver'ı PATH'e ekleyin veya proje klasörüne kopyalayın

6. Konfigürasyon:
   - `src/config.py` dosyasını düzenleyerek gerekli ayarları yapın
   - WordPress API bilgilerinizi güncelleyin

7. Uygulamayı çalıştırın:
   ```bash
   python -m uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
   ```

## Kullanım

Crawler'ı başlatmak için:
```bash
python -m uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
```

Log dosyalarını `crawler.log` dosyasında takip edebilirsiniz.
