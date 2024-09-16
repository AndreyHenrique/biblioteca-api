import requests
import json

"""
url = 'http://localhost:8080/autores'
autor = {
    "nome": "Andrey Henrique",
    "nacionalidade": "Brasileira",
    "data_nascimento": "2005-01-14"
}

response = requests.post(url, json=autor)

if response.status_code == 201:
    print("Autor adicionado com sucesso!")
    print("Resposta:", response.json())
else:
    print(f"Erro ao adicionar autor: {response.status_code}")
    print("Mensagem:", response.json())
"""

livro = {  'titulo': 'A arte da guerra',
            'genero': 'fantasia',
            'ano': '2005',}

autor = {'nome': 'josé'}

url = 'http://localhost:8080/autores/1/livros/1'

response = requests.post(url)


print("Resposta:", response.json())
