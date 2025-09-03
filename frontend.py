import os
import streamlit as st
from dotenv import load_dotenv
from agente import agente_recomendador, JogosRecomendado
from st_clickable_images import clickable_images
import webbrowser


load_dotenv()

st.title("Recomendador de jogos")

ultimos_games = st.text_area("Conte para mim os últimos cinco jogos que você comprou...",
                             height=300)

generos = [
    "Single Player", "Action", "Adventure", "Indie", "Multiplayer",
    "RPG", "Simulation", "Strategy", "Third Person", "Bird View",
    "First Person", "Side View", "Co-op", "FPS/TPS", "Horror",
    "Sport", "Racing", "Platform", "Split Screen", "Local co-op",
    "Puzzle", "Virtual Reality", "Fighting", "Point & Click",
    "Hack & Slash", "Arcade", "MMO", "Massive Multiplayer", "Music", "Educational"
]

generos.sort()

# Multiselect com limite de 5 opções
generos_escolhidos = st.multiselect(
    "Selecione até 5 gêneros de jogos que você mais gosta:",
    generos,
    max_selections=5  # limite máximo
)

valor_min, valor_max = st.slider(
    "Selecione a faixa de preço para o seu próximo jogo (em Reais):",
    min_value=0,
    max_value=500,
    value=(80, 150)  # valor inicial do range (min, max) default
)


# Inicializa session_state se ainda não existir
if "lista_thumbs" not in st.session_state:
    st.session_state.lista_thumbs = []
if "title_thumbs" not in st.session_state:
    st.session_state.title_thumbs = []
if "link_thumbs" not in st.session_state:
    st.session_state.link_thumbs = []
if "lista_justificativas" not in st.session_state:
    st.session_state.lista_justificativas = []


if st.button("Encontrar meus próximos jogos"):
    with st.spinner("Procurando os melhores jogos para você...", show_time=True):
        for chunk in agente_recomendador.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Últimos jogos adquiridos: {ultimos_games}\n
                        Generos preferidos: {generos_escolhidos}\n
                        Faixa de preço em reais: {valor_min} - {valor_max}""",
                    }
                ]
            },
        ):
            with open('agent_output.txt', 'a', encoding='utf-8') as f:
                f.write(f"{chunk}\n")
                if "agent" in chunk:
                    for msg in chunk["agent"]["messages"]:
                        print(f"\nAgente: ")
                        print(f"Conteúdo: {msg.content if msg.content != "" else 'N/A'}")
                        print(f"Atributos adicionais: {msg.additional_kwargs}")
                if "generate_structured_response" in chunk:
                    answer = chunk["generate_structured_response"]["structured_response"]
                    print("Resposta final gerada pelo agente")

                    # Atualiza session_state com os resultados
                    st.session_state.lista_thumbs = [j.miniatura for j in answer.lista_jogos]
                    st.session_state.title_thumbs = [j.titulo for j in answer.lista_jogos]
                    st.session_state.link_thumbs = [j.link for j in answer.lista_jogos]
                    st.session_state.lista_justificativas = [j.justificativa for j in answer.lista_jogos]
        
# Mostra recomendações se já houver
if st.session_state.lista_thumbs:
    st.markdown("## Jogos Recomendados")
    clicked = clickable_images(
        paths=st.session_state.lista_thumbs,
        titles=st.session_state.lista_justificativas,
        div_style={
            "display": "grid",
            "grid-template-columns": "repeat(3, 1fr)",  # 3 colunas iguais
            "gap": "10px",  # espaço entre as imagens
            "justify-items": "center"  # centraliza as thumbs em cada célula
        },
        img_style={"margin": "5px", "height": "auto", "width": "210px", "object-fit": "cover"},
    )

    # st.markdown(f"{st.session_state.lista_justificativas[clicked]}" if clicked > -1 else "No image clicked")
    if clicked > -1:
        webbrowser.open_new_tab(st.session_state.link_thumbs[clicked])

