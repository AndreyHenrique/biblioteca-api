from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Dicionário dos autores
autores = {}
# Variável que serve gerar os IDs na adição do autor
contador_id_autor = 1

# Criando a classe para o servidor REST
class ServidorREST(BaseHTTPRequestHandler):

    # Função da Naila para implementar cabeçalho(N entendi)
    def definir_cabecalho(self, status_do_codigo = 200):
        self.send_response(status_do_codigo)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    # Função da Naila de separar a URL    
    def caminho_URL(self):
        partes_URL = self.path.split('/')
        return partes_URL

# Função GET
    def do_GET(self):
        caminho = self.caminho_URL()  
        # Mostrar todos os autores
        if self.path == '/authors':  
            self.definir_cabecalho(200)
            self.wfile.write(json.dumps(list(autores.values())).encode())
        # Mostrar autor específico pelo ID    
        elif len(caminho) == 3 and caminho[1] == 'authors':
            try:
                id_autor = int(caminho[2]) 
                autor = autores.get(id_autor)
                if autor:
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(autor).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função POST
    def do_POST(self):
        global contador_id_autor
        if self.path == '/authors':
            comprimento_informacao = int(self.headers['Content-Length'])
            dados_adicionados = self.rfile.read(comprimento_informacao)
            novo_autor = json.loads(dados_adicionados)
            nome = novo_autor.get("nome")
            # Caso o usuario não informe a nacionalidade ou a data de nascimento, ficará como "Desconhecido"
            nacionalidade = novo_autor.get("nacionalidade", "Desconhecido")
            data_nascimento = novo_autor.get("data_nascimento", "Desconhecido")
            if not nome:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'O nome é obrigatório'}).encode())
                return
            autor_id = contador_id_autor
            contador_id_autor += 1
            autor = {
                "id" : autor_id,
                "nome": nome,
                "nacionalidade": nacionalidade,
                "data_nascimento": data_nascimento
            }
            autores[autor_id] = autor
            self.definir_cabecalho(201)
            self.wfile.write(json.dumps(autor).encode())
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função PUT (atualiza um autor que ja existe)
    def do_PUT(self):
        caminho = self.caminho_URL()
        if len(caminho) == 3 and caminho[1] == 'authors':
            try:
                id_autor = int(caminho[2])
                if id_autor in autores:
                    comprimento_informacao = int(self.headers['Content-Length'])
                    put_data = self.rfile.read(comprimento_informacao)
                    dados_atualizados = json.loads(put_data)
                    autores[id_autor].update(dados_atualizados)
                    autor = autores[id_autor]
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(autor).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função DELETE
    def do_DELETE(self):
        caminho = self.caminho_URL()
        if len(caminho) == 3 and caminho[1] == 'authors':  
            try:
                id_autor = int(caminho[2]) 
                if id_autor in autores:
                    del autores[id_autor]
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps({'message': 'Autor removido'}).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

# Função para rodar o servidor HTTP
def rodando_servidor():
    endereco_servidor = ('localhost', 8080)
    httpd = HTTPServer(endereco_servidor, ServidorREST)
    print(f'Servidor rodando em http://{endereco_servidor[0]}:{endereco_servidor[1]}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Servidor interrompido")
        httpd.server_close()

# Iniciar o servidor quando o script for executado diretamente
if __name__ == '__main__':
    rodando_servidor()