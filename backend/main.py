import feedparser
import uvicorn
import requests
import xml.etree.ElementTree as ET
from fastapi.responses import Response
from fastapi import FastAPI, HTTPException
from backend.routers import eneba


URL_ENEBA = "https://www.eneba.com/rss/products.xml?influencer_id=FlaGamer29"

app = FastAPI(
    title="Eneba API",
    description="API para interagir com o feed de produtos da Eneba",
    version="1.0.0"
)

app.include_router(eneba.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


