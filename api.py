from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crawlers.hepsiburada_crawler import HepsiburadaCrawler
import uvicorn
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="Hepsiburada Crawler API",
    description="Hepsiburada ürün bilgilerini çekmek için API",
    version="1.0.0"
)

class CrawlRequest(BaseModel):
    url: str

@app.post("/crawl")
async def crawl_product(request: CrawlRequest):
    try:
        crawler = HepsiburadaCrawler(request.url)
        result = crawler.crawl()
        return result
    except Exception as e:
        logging.error(f"Crawl işlemi sırasında hata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hepsiburada Crawler API'ye Hoş Geldiniz!"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 