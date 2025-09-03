import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
from prompts import PROMPT_RECOMENDADOR
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


load_dotenv()


@tool
def filtrar_jogo(titulo: str):
    """Utilize esta função para recuperar informações como titulo, descrição, links de afiliado 
    e o identificador de um jogo presente na base da eneba"""

    url_filter_games = f"http://127.0.0.1:8000/eneba/filter_games"

    response = requests.get(url_filter_games,
                            params={"title": titulo})
    
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            return {"error": f"Erro ao decifrar a resposta. {e}"}
    else:
        return {"error": "Jogo não encontrado"}
    
@tool
def listar_jogos_por_preco(min_price: float, max_price: float):
    """Utilize esta função para recuperar informações sobre jogos na faixa de preço especificada"""
    url_listar_jogos_por_preco = f"http://127.0.0.1:8000/eneba/list_games_by_price"

    response = requests.get(url_listar_jogos_por_preco,
                            params={"min_price": min_price, "max_price": max_price})

    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            return {"error": f"Erro ao decifrar a resposta. {e}"}
    else:
        return {"error": "Nenhum jogo encontrado"}
    
@tool
def get_genero_jogo_por_id(id: str):
    """Utilize esta função para recuperar informações sobre a descrição e o gênero de um jogo pelo seu ID"""
    url_get_genero_jogo = f"http://127.0.0.1:8000/eneba/get_gender_by_id"

    response = requests.get(url_get_genero_jogo,
                            params={"id": id})

    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            return {"error": f"Erro ao decifrar a resposta. {e}"}
    else:
        return {"error": "Jogo não encontrado"}
    
@tool
def convert_real_to_euro(valor_em_reais: float):
    """Utilize esta função para converter o valor fornecido pelo usuário em reais para euros"""
    url_exchange = "https://api.exchangeratesapi.io/v1/latest"

    # Testar se já tem um arquivo salvo com os parâmetros de conversão.
    # Se existir os arquivos, vai carregar o que já foi executado.
    # Caso já tenha executado no mesmo dia da geração do arquivo, irá carregar a taxa de conversão sem fazer requisição a API
    # Caso o arquivo exista e a data não seja a mesma, irá fazer a requisição a API para atualizar a taxa de conversão.

    # Consulte a documentação da API utilizada desta função neste link: https://exchangeratesapi.io/documentation/

    if os.path.exists("exchange_rates.json"):
        with open("exchange_rates.json", "r") as f:
            exchange_rates = json.load(f)
            if exchange_rates["date"] != datetime.now().strftime("%Y-%m-%d"):
                print(f"Buscando valor {valor_em_reais} em euros")
                response = requests.get(url_exchange,
                                        params={"access_key": os.getenv("EXCHANGE_RATES_API_KEY"),
                                                "symbols": "BRL",
                                                "format": 1})
                if response.status_code == 200:
                    exchange_rates = response.json()
                    with open("exchange_rates.json", "w") as f:
                        json.dump(exchange_rates, f)
            print(f"Carregando cotação do euro do dia...")
            taxa_conversao = exchange_rates["rates"]["BRL"]
    else:
        ### Primeira execução da função - quando não existe o arquivo
        print(f"Buscando valor {valor_em_reais} em euros")
        response = requests.get(url_exchange,
                                params={"access_key": os.getenv("EXCHANGE_RATES_API_KEY"),
                                        "symbols": "BRL",
                                        "format": 1})
        print(response.status_code)
        if response.status_code == 200:
            exchange_rates = response.json()
            with open("exchange_rates.json", "w") as f:
                json.dump(exchange_rates, f)
            taxa_conversao = exchange_rates["rates"]["BRL"]  
        else:
            print(response)
            return {"error": "Erro ao obter taxas de câmbio"}
            

    return {"valor_em_euros": round(float(valor_em_reais) / taxa_conversao, 2)}

@tool
def convert_euro_to_reais(valor_em_euros: float):
    """Utilize esta função para converter o valor de euros para reais"""
    url_exchange = "https://api.exchangeratesapi.io/v1/latest"

    # Testar se já tem um arquivo salvo com os parâmetros de conversão.
    # Se existir os arquivos, vai carregar o que já foi executado.
    # Caso já tenha executado no mesmo dia da geração do arquivo, irá carregar a taxa de conversão sem fazer requisição a API
    # Caso o arquivo exista e a data não seja a mesma, irá fazer a requisição a API para atualizar a taxa de conversão.

    # Consulte a documentação da API utilizada desta função neste link: https://exchangeratesapi.io/documentation/

    if os.path.exists("exchange_rates.json"):
        with open("exchange_rates.json", "r") as f:
            exchange_rates = json.load(f)
            if exchange_rates["date"] != datetime.now().strftime("%Y-%m-%d"):
                print(f"Buscando valor {valor_em_euros} em euros")
                response = requests.get(url_exchange,
                                        params={"access_key": os.getenv("EXCHANGE_RATES_API_KEY"),
                                                "symbols": "BRL",
                                                "format": 1})
                if response.status_code == 200:
                    exchange_rates = response.json()
                    with open("exchange_rates.json", "w") as f:
                        json.dump(exchange_rates, f)
            print(f"Carregando cotação do real do dia...")
            taxa_conversao = exchange_rates["rates"]["BRL"]
    else:
        ### Primeira execução da função - quando não existe o arquivo
        print(f"Buscando valor {valor_em_euros} em euros")
        response = requests.get(url_exchange,
                                params={"access_key": os.getenv("EXCHANGE_RATES_API_KEY"),
                                        "symbols": "BRL",
                                        "format": 1})
        print(response.status_code)
        if response.status_code == 200:
            exchange_rates = response.json()
            with open("exchange_rates.json", "w") as f:
                json.dump(exchange_rates, f)
            taxa_conversao = exchange_rates["rates"]["BRL"]  
        else:
            print(response)
            return {"error": "Erro ao obter taxas de câmbio"}
            

    return {"valor_em_reais": round(float(valor_em_euros) * taxa_conversao, 2)}

@tool
def link_valido_eneba(link: str):
    "Use esta função para validar se o link de afiliação da Eneba é válido"
    response = requests.get(link)
    if response.status_code == 200 and "eneba.com" in link:
        return True
    else:
        return False
    
# Classe para representar a estrutura de saída do jogo recomendado pelo agente
class TituloRecomendado(BaseModel):
    titulo: str
    genero: str
    preco: float
    link: str
    miniatura: str = Field("Link da miniatura do jogo na Eneba")
    justificativa: str

class JogosRecomendado(BaseModel):
    lista_jogos: List[TituloRecomendado]

prompt_recomendador_template = ChatPromptTemplate.from_messages([
    ("system", PROMPT_RECOMENDADOR),
    ("human", """Últimos jogos adquiridos: {jogos_adq}\n
                Generos preferidos: {generos_preferidos}\n
                Faixa de preço: {faixa_preco_minima} - {faixa_preco_maxima}"""),
    MessagesPlaceholder("agent_scratchpad"),
])


agente_recomendador = create_react_agent(
    model="openai:gpt-4o-mini",
        tools=[
        filtrar_jogo,
        listar_jogos_por_preco,
        get_genero_jogo_por_id,
        convert_real_to_euro,
        convert_euro_to_reais,
        link_valido_eneba
    ],
    prompt=(
        PROMPT_RECOMENDADOR
    ),
    name="agente_recomendador",
    response_format=JogosRecomendado
)


# Testando o agente

# jogos_adq = "assetto corsa, gran turismo 7, grid motorsport, life is strange 2, gta definitve edition"
# generos_preferidos = "racing, sports, single player"
# faixa_preco_minima = 50
# faixa_preco_maxima = 80




# for chunk in agente_recomendador.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": f"""Últimos jogos adquiridos: {jogos_adq}\n
#                 Generos preferidos: {generos_preferidos}\n
#                 Faixa de preço em reais: R$ {faixa_preco_minima} - R$ {faixa_preco_maxima}""",
#             }
#         ]
#     },
# ):
#     with open('agent_output.txt', 'a', encoding='utf-8') as f:
#         f.write(f"{chunk}\n")
#         if "agent" in chunk:
#             for msg in chunk["agent"]["messages"]:
#                 print(f"\nAgente: ")
#                 print(f"Conteúdo: {msg.content if msg.content != "" else 'N/A'}")
#                 print(f"Atributos adicionais: {msg.additional_kwargs}")
#         if "generate_structured_response" in chunk:
#             print(f"\n=== Resposta Estruturada ===")
#             print(type(chunk["generate_structured_response"]["structured_response"]))
#             print(chunk["generate_structured_response"]["structured_response"])



