# eneba-gaming-recomendation
![Interface da solução](https://github.com/LucasSoares29/eneba-gaming-recomendation/blob/main/pic1.png)
Projeto que usa agentes de IA construidos no LangChain para recomendar jogos presentes na feed RSS do Eneba. O FastAPI também foi usado no projeto para construir as rotas para serem chamadas como tools do Agente. 

# 🚀 Setup do Projeto

## 1 - Criar a máquina virtual
```bash
python -m venv <nome_da_venv>
```

## 2 - Ativar a máquina virtual

Windows:
```
<nome_da_venv>\Scripts\activate.bat
```

Linux/Mac:
```
source <nome_da_venv>/bin/activate
```

## 3 - Instalar as dependências

```
pip install -r requirements.txt
```

## 4 - Configurar variáveis de ambiente

Crie um arquivo .env na raiz do projeto e adicione as chaves de acesso:

```
OPENAI_API_KEY=
TAVILY_API_KEY=
EXCHANGE_RATES_API_KEY=
```

As chaves da OpenAI podem ser geradas [aqui](https://platform.openai.com/account/api-keys)  
As chaves da Tavily podem ser geradas [aqui](https://app.tavily.com/home)  
As chaves da Exchange Rates, usadas para conversão de preços, podem ser geradas [aqui](https://exchangeratesapi.io/)  

## 5 - Executar o backend
```
uvicorn backend.main:app --reload
```

## 6 - Executar o frontend

Abra um novo terminal na raiz do projeto:
```
streamlit run frontend.py
```

# 📌 TO DO (Melhorias Futuras)

1. Implementar uma estrutura multiagente para melhorar as recomendações.

2. Realizar fine-tuning no modelo de inferência de gêneros de jogos.

3. Desenvolver notificações no Discord com recomendações personalizadas.
