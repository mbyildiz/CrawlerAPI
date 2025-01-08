from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from crawlers.hepsiburada_crawler import HepsiburadaCrawler

app = FastAPI(title="E-Commerce Crawler API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "E-Commerce Crawler API'ye Hoş Geldiniz",
        "supported_services": ["hepsiburada"]
    }

@app.get("/crawl")
def crawl_product(url: str, service: str = "hepsiburada"):
    try:
        if service.lower() == "hepsiburada":
            crawler = HepsiburadaCrawler(url)
            content = crawler.crawl()
            return {
                "status": "success",
                "service": service,
                "data": content
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Şu anda {service} servisi desteklenmemektedir. Desteklenen servisler: ['hepsiburada']"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 