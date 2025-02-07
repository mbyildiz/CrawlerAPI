# Hepsiburada Crawler API

Bu proje, Hepsiburada'dan ürün bilgilerini çekmek için geliştirilmiş bir REST API'dir.

## Özellikler

- Ürün başlığı ve marka bilgisi
- Ürün fiyatı
- Ürün açıklaması
- Ürün görselleri
- Kategori bilgisi
- Swagger dokümantasyonu

## Kurulum

1. Projeyi klonlayın:
```bash
git clone [repo-url]
cd [proje-dizini]
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

## API'yi Çalıştırma

API'yi başlatmak için:

```bash
python api.py
```

API varsayılan olarak http://localhost:8000 adresinde çalışacaktır.

## API Kullanımı

### Swagger Dokümantasyonu

API dokümantasyonuna erişmek için tarayıcınızda şu adresi açın:
```
http://localhost:8000/docs
```

### Endpoint'ler

1. Ana Sayfa
- Method: GET
- URL: http://localhost:8000/
- Yanıt: Karşılama mesajı

2. Ürün Bilgisi Çekme
- Method: POST
- URL: http://localhost:8000/crawl
- Body örneği:
```json
{
    "url": "https://www.hepsiburada.com/[urun-url]"
}
```
- Yanıt örneği:
```json
{
    "title": "Ürün Adı",
    "brand": "Marka Adı",
    "price": "1.234,56 TL",
    "description": "Ürün açıklaması",
    "image_url": "https://...",
    "additional_images": ["https://...", "..."],
    "categories": ["Kategori1", "Kategori2"],
    "content": "Detaylı açıklama"
}
```

## Test Etme

API'yi test etmek için aşağıdaki yöntemleri kullanabilirsiniz:

1. Swagger UI
- http://localhost:8000/docs adresine gidin
- /crawl endpoint'ini seçin
- "Try it out" butonuna tıklayın
- URL'yi girin ve "Execute" butonuna tıklayın

2. cURL ile test:
```bash
curl -X POST "http://localhost:8000/crawl" \
     -H "Content-Type: application/json" \
     -d '{"url":"https://www.hepsiburada.com/[urun-url]"}'
```

3. Python ile test:
```python
import requests

url = "http://localhost:8000/crawl"
data = {
    "url": "https://www.hepsiburada.com/[urun-url]"
}
response = requests.post(url, json=data)
print(response.json())
```

## Hata Yönetimi

API hata durumlarında uygun HTTP durum kodları ile birlikte hata mesajları döndürür:
- 500: Sunucu hatası (crawling işlemi sırasında oluşan hatalar)
- 422: Geçersiz istek (URL formatı hatalı vb.)

## Logging

API'nin çalışması sırasında oluşan loglar `api.log` dosyasında tutulur. Bu dosyada:
- Başarılı istekler
- Hata durumları
- Crawling işlem detayları
gibi bilgileri bulabilirsiniz.
