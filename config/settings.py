"""
Crawler ayarları için yapılandırma dosyası
"""

# Hepsiburada Crawler Ayarları
HEPSIBURADA_SETTINGS = {
    # Sayfa yükleme ayarları
    'page_load_wait': 2,  # Sayfa yüklenmesi için bekleme süresi (saniye)
    
    # Scroll ayarları
    'scroll_wait': 0.5,  # Scroll işlemleri arası bekleme süresi (saniye)
    'scroll_step_ratio': 0.5,  # Sayfa yüksekliğinin yüzde kaçı kadar scroll yapılacak (0-1 arası)
    
    # Element bekleme ayarları
    'element_wait': 5,  # Elementlerin yüklenmesi için maksimum bekleme süresi (saniye)
    'detail_tab_wait': 1,  # Detay sekmesi tıklama sonrası bekleme süresi (saniye)
    
    # Debug ayarları
    'save_debug_html': True,  # Debug için HTML kaydetme
    'debug_file_path': 'debug_page.html',  # Debug dosyası yolu
    
    # Selenium ayarları
    'headless': True,  # Başsız mod
    'window_size': (1920, 1080),  # Pencere boyutu
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Diğer crawler'lar için benzer ayarlar eklenebilir
# TRENDYOL_SETTINGS = { ... }
# N11_SETTINGS = { ... } 