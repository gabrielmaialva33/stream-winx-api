import requests

from core import config
from openai import OpenAI

client = OpenAI(
    api_key=config.OPENAI_API_KEY
)


def call_get_top_post_api():
    url = "http://127.0.0.1:8000/api/v1/top/post"  # Atualize para seu endereço real
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_top_post",
            "description": "Obtém o melhor post disponível, baseado no número de reações.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

persona = {
    "role": "system",
    "content": (
        "Você é CineWinx, uma assistente virtual que ajuda os usuários a encontrar filmes e séries para assistir. "
        "Você é apaixonada por cinema e está sempre pronta para recomendar os melhores títulos para os usuários. "
        "Você é amigável, prestativa e está sempre disposta a ajudar."

    )
}


def get_chat_response(prompt):
    completion = client.chat.completions.create(
        # model="chatgpt-4o-latest",
        model="gpt-4o",
        messages=[
            {"role": "system", "content": persona["content"]},
            {"role": "user", "content": prompt}
        ],
        temperature=1,
        tools=tools
    )

    response = completion.choices[0].message

    print(response)
    # Verificar se foi feita uma chamada de função
    if response.get("tool_calls"):
        tool_call = response["tool_calls"][0]
        if tool_call.get("function").get("name") == "get_top_post":
            # Chamar o endpoint diretamente
            top_post = call_get_top_post_api()  # Implemente uma função para chamar o endpoint

            return {
                "type": "tool_response",
                "message": f"O melhor filme é: {top_post['original_content']}",
                "data": top_post
            }

    return response
