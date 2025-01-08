import asyncio
from crawlers.hepsiburada_crawler import HepsiburadaCrawler
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
import sys

# Rich console oluştur
console = Console()

# Logging ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crawler.log')
    ]
)

async def test_crawler():
    test_url = "https://www.hepsiburada.com/bosch-25-li-pro-vidalama-seti-2607017037-pm-HB00000WQZEQ"
    
    try:
        with console.status("[bold green]Veri çekiliyor... (Tarayıcı açılacak)") as status:
            crawler = HepsiburadaCrawler(test_url)
            content = await crawler.crawl()
            
            if not content:
                raise Exception("Sayfa içeriği alınamadı!")
                
            # Ürün bilgileri tablosu
            table = Table(title="Ürün Detayları", show_header=True, header_style="bold magenta")
            table.add_column("Özellik", style="cyan")
            table.add_column("Değer", style="green", overflow="fold")
            
            # Temel bilgileri tabloya ekle
            table.add_row("Başlık", content['title'])
            table.add_row("Fiyat", content['price'])
            table.add_row("Kategori", ", ".join(content['categories']))
            table.add_row("Görsel Sayısı", str(len(content.get('additional_images', [])) + 1))
            
            # Tabloyu göster
            console.print("\n")
            console.print(table)
            
            # Ürün açıklamasını panel içinde göster
            if content.get('description'):
                console.print("\n[bold cyan]Ürün Açıklaması:[/bold cyan]")
                console.print(Panel(
                    content['description'][:500] + "..." if len(content['description']) > 500 else content['description'],
                    title="Detaylar",
                    border_style="green"
                ))
            
            # Görselleri listele
            if content.get('image_url'):
                console.print("\n[bold cyan]Görsel URL'leri:[/bold cyan]")
                for i, img in enumerate([content['image_url']] + content.get('additional_images', []), 1):
                    if img:
                        rprint(f"[dim]#{i}[/dim] [link={img}]{img}[/link]")
                
    except Exception as e:
        console.print(f"[bold red]Hata oluştu:[/bold red] {str(e)}", style="red")
        logging.error(f"Hata oluştu: {str(e)}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(test_crawler())
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\nBeklenmeyen hata: {str(e)}") 