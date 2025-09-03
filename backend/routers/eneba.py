from typing import List
import feedparser
import requests
import os
import xml.etree.ElementTree as ET
from fastapi.responses import Response
from fastapi import HTTPException, APIRouter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from fastapi.responses import JSONResponse

load_dotenv()

router = APIRouter(
    tags=['Eneba'],
    prefix="/eneba"  # Prefixo para todas as rotas deste router
)

URL_ENEBA = "https://www.eneba.com/rss/products.xml?influencer_id=FlaGamer29"

def summarize_game_description(description: str) -> str:
        if description is not None:
            llm = ChatOpenAI(model="gpt-4o-mini",
                            temperature=0.25,
                            api_key=os.getenv("OPENAI_API_KEY")
            )

            prompt = """

                You're a gaming expert. Your job is to summarize a game description up to 300 words

                Description: {descricao}
                
            """

            prompt_template = PromptTemplate(input_variables=['descricao'],
                                        template=prompt,
            )

            chain = prompt_template | llm | StrOutputParser()

            if description:
                len_words = len(description.split())
                if len_words > 300:
                    descricao_resumida = chain.invoke({"descricao": description})
                else:
                    descricao_resumida = description

            return descricao_resumida
        else:
            return ""


@router.get('/list_games')
async def list_games(qtd_games: int = 10):
    """
        Retorna a quantidade de jogos do feed do eneba requisitado pelo usuário entre 1 a 100 jogos
    
    """

    global URL_ENEBA

    feed = feedparser.parse(URL_ENEBA)

    if 1 <= qtd_games <= 100:
        return {
            "games": [
                {
                    "title": entry.title,
                    "link": entry.link,
                    "thumbnail": entry.g_image_link,
                    "availability": entry.g_availability,
                    "price": entry.g_price,
                    "product_category": entry.g_google_product_category,
                    "g_brand": entry.g_brand,
                    "region": entry.region
                }
                for entry in feed.entries[:qtd_games]
            ],
        }
    else:
        raise HTTPException(status_code=400, detail="Quantidade inválida")


@router.get("/filter_games", response_class=Response)
async def filter_games(title: str):
    """
        Retorna informações sobre os jogos da base XML dada a palavra-chave informada pelo usuário
    
    """

    global URL_ENEBA

    # Baixa a XML da URL
    resp = requests.get(URL_ENEBA)
    resp.raise_for_status()
    xml_content = resp.content

    root = ET.fromstring(xml_content)

    # Namespace usado no feed
    ns = {"g": "http://base.google.com/ns/1.0"}

    # Filtra apenas os itens que tenham o título inserido pelo usuário
    itens_filtrados = []
    for item in root.findall(".//item"):
        titulo = item.find("title")
        if titulo is not None and title.lower() in titulo.text.lower():
            itens_filtrados.append(item)


    # Se não encontrar nada, retorna resposta vazia
    if not itens_filtrados:
        raise HTTPException(status_code=404, detail="Nenhum item encontrado")
    
    # Montando o JSON de saída
    results = []
    for item in itens_filtrados:
        results.append({
            "id": item.find("g:id", ns).text if item.find("g:id", ns) is not None else None,
            "sku": item.find("sku").text if item.find("sku") is not None else None,
            "title": item.find("title").text if item.find("title") is not None else None,
            # "original_title": item.find("original_title", ns).text if item.find("original_title") is not None else None,
            "description": item.find("g:description", ns).text if item.find("g:description", ns) is not None else None,
            "link": item.find("link").text if item.find("link") is not None else None,
            "image_link": item.find("g:image_link", ns).text if item.find("g:image_link", ns) is not None else None,
            "availability": item.find("g:availability", ns).text if item.find("g:availability", ns) is not None else None,
            "price": item.find("g:price", ns).text if item.find("g:price", ns) is not None else None,
            # "google_product_category": item.find("g:google_product_category", ns).text if item.find("g:google_product_category", ns) is not None else None,
            # "product_type": item.find("g:product_type", ns).text if item.find("g:product_type", ns) is not None else None,
            # "brand": item.find("g:brand", ns).text if item.find("g:brand", ns) is not None else None,
            # "region": item.find("region").text if item.find("region") is not None else None,
            # "condition": item.find("g:condition", ns).text if item.find("g:condition", ns) is not None else None,
            # "identifier_exists": item.find("g:identifier_exists", ns).text if item.find("g:identifier_exists", ns) is not None else None,
        })
    
    if results:
        return JSONResponse(content={"items": results})


@router.get("/list_games_by_price", response_class=Response)
async def list_games_by_price(min_price: float, max_price: float):
    """
        Retorna informações sobre os jogos da base XML que respeitam a faixa de preço informada (em Euros) - EUR
        tais como ID, Titulo, Link de afiliado, Miniatura e Preço.
    
    """

    global URL_ENEBA

    # Baixa a XML da URL
    resp = requests.get(URL_ENEBA)
    resp.raise_for_status()
    xml_content = resp.content

    root = ET.fromstring(xml_content)

    # Namespace usado no feed
    ns = {"g": "http://base.google.com/ns/1.0"}

    # Filtra apenas os itens que tenham o título inserido pelo usuário
    itens_filtrados = []
    for item in root.findall(".//item"):
        price_tag = item.find("g:price", ns)

        if price_tag is not None:
            price_text = price_tag.text  # 5.50 EUR
            price = float(price_text.split(" EUR")[0]) # 5.50
        if min_price <= price <= max_price:
            itens_filtrados.append(item)

    # Se não encontrar nada, retorna resposta vazia
    if not itens_filtrados:
        raise HTTPException(status_code=404, detail="Nenhum item encontrado")
    
    # Ordenar por preço na ordem crescente
    itens_filtrados.sort(key=lambda x: float(x.find("g:price", ns).text.split(" EUR")[0]))

    # Montando o JSON de saída
    results = []
    for item in itens_filtrados:

        # Resumir descrição usando LLM
        # print(f"Gerando descrição do jogo {item.find('title').text}")
        # descricao_resumida = summarize_game_description(item.find("g:description", ns).text)

        results.append({
            "id": item.find("g:id", ns).text if item.find("g:id", ns) is not None else None,
            # "sku": item.find("sku").text if item.find("sku") is not None else None,
            "title": item.find("title").text if item.find("title") is not None else None,
            # "original_title": item.find("original_title", ns).text if item.find("original_title") is not None else None,
            # "description": descricao_resumida if descricao_resumida is not None else None,
            "link": item.find("link").text if item.find("link") is not None else None,
            "image_link": item.find("g:image_link", ns).text if item.find("g:image_link", ns) is not None else None,
            # "availability": item.find("g:availability", ns).text if item.find("g:availability", ns) is not None else None,
            "price": item.find("g:price", ns).text if item.find("g:price", ns) is not None else None,
            # "google_product_category": item.find("g:google_product_category", ns).text if item.find("g:google_product_category", ns) is not None else None,
            # "product_type": item.find("g:product_type", ns).text if item.find("g:product_type", ns) is not None else None,
            # "brand": item.find("g:brand", ns).text if item.find("g:brand", ns) is not None else None,
            # "region": item.find("region").text if item.find("region") is not None else None,
            # "condition": item.find("g:condition", ns).text if item.find("g:condition", ns) is not None else None,
            # "identifier_exists": item.find("g:identifier_exists", ns).text if item.find("g:identifier_exists", ns) is not None else None,
        })
    
    if results:
        return JSONResponse(content={"items": results})


@router.get("/get_gender_by_id")
def get_gender_by_id(id: str):
    """
        Através de uma chamada ao modelo de LLM, uma vez que a informação de gênero  
        do jogo está ausente na base XML da Eneba, através do identificador único
        do título do game, ele buscará as informações de título e descrição e o modelo
        de inteligência artificial irá inferir os gêneros em palavras-chaves.
    
    """

    global URL_ENEBA

    # Baixa a XML da URL
    resp = requests.get(URL_ENEBA)
    resp.raise_for_status()
    xml_content = resp.content

    root = ET.fromstring(xml_content)

    # Namespace usado no feed
    ns = {"g": "http://base.google.com/ns/1.0"}

    # Filtra apenas os itens que tenham o título inserido pelo usuário
    itens_filtrados = []
    for item in root.findall(".//item"):
        identifier = item.find("g:id", ns)

        if identifier is not None and identifier.text == id:
            itens_filtrados.append(item)
            titulo = item.find("title")
            descricao = item.find("g:description", ns) if item.find("g:description", ns) is not None else None

    # Se não encontrar nada, retorna resposta vazia
    if not itens_filtrados:
        raise HTTPException(status_code=404, detail="Nenhum item encontrado")
    
    # Chamada ao modelo de LLM
    llm = ChatOpenAI(model="gpt-4o-mini",
                     temperature=0.7,
                     api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = """
        You're a gaming expert. Your mission is classify the game based on its title and description.
        It's possible to infer more than one gender. 
        
        Rules:
        - Sort by the most relevant gender to least relevant gender.
        - Respect the list of these possible genders: Single Player, Action, Adventure, Indie, Multiplayer,
        RPG, Simulation, Strategy, Third Person, Bird View, First Person, Side View, Co-op, FPS/TPS, Horror,
        Sport, Racing, Platform, Split Screen, Local co-op, Puzzle, Virtual Reality, Fighting, Point & Click,
        Hack & Slash, Arcade, MMO, Massive Multiplayer, Music, Educational.
        - Up to 5 genres can be inferred.
        - If description is None or empty, infer the gender by the game title and create a short description up to 200 
        characters about the game

        - The output MUST BE in JSON Format following this schema:

        {{ 
            'title': str
            'description': str
            'game_gender': List[str]
        }}

        Input:
        Title: {titulo}
        Description: {descricao}
        
    """

    # Definindo a estrutura do Json de saída do modelo
    class GameGender(BaseModel):
        title: str = Field(description="Titulo do jogo na base XML da eneba")
        description: str = Field(description="Descricao do jogo na base XML da eneba")
        game_gender: List[str] = Field(description="Generos do jogo inferidos pelo modelo")

    prompt_template = PromptTemplate(input_variables=['titulo', 'descricao'],
                                     template=prompt,
                                     output_parser=JsonOutputParser(pydantic_object=GameGender)
    )

    chain = prompt_template | llm | JsonOutputParser(pydantic_object=GameGender)
    
    response = chain.invoke({"titulo": titulo.text, "descricao": descricao.text})

    with open('output_llm.txt', 'w', encoding='utf-8') as f:
        f.write(str(response))

    return response # FastAPI converte dict pra JSON automaticamente.