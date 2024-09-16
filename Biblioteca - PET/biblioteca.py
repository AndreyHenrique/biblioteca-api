from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Banco de dados
autores = {}
livros = {}
associacoes = {}
contador_id_autor = 1
contador_id_livro = 1

# Classe para o servidor REST
class ServidorREST(BaseHTTPRequestHandler):

    # Função para implementar cabeçalho HTTP ao cliente
    def definir_cabecalho(self, status_do_codigo = 200):
        self.send_response(status_do_codigo)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    # Função para separar a URL    
    def caminho_URL(self):
        partes_URL = self.path.split('/')
        return partes_URL
    
    # Função POST (Adiciona um novo autor ou um novo livro)
    def do_POST(self):
        global contador_id_autor, contador_id_livro
        caminho = self.caminho_URL()

        # POST de autores
        if self.path == '/autores':
            # Recupera conteúdo e tamanho da requisição
            comprimento_informacao = int(self.headers['Content-Length'])
            dados_adicionados = self.rfile.read(comprimento_informacao)
            # Recupera informações do POST
            dados_autor = json.loads(dados_adicionados)

            # Cria autor
            novo_autor = {
                'id': contador_id_autor,
                'nome': dados_autor.get('nome'),
                'nacionalidade': dados_autor.get('nacionalidade', 'desconhecido'),
                'data_nascimento': dados_autor.get('data_nascimento', 'desconhecido'),
            }

            # Verifica se o nome do autor está na requisição
            if not novo_autor['nome']:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'O nome é obrigatório'}).encode())
                return
            
            autores[contador_id_autor] = novo_autor
            contador_id_autor += 1
            self.definir_cabecalho(201)
            self.wfile.write(json.dumps(novo_autor).encode())

        # POST de livros
        elif self.path == '/livros':
            # Recupera conteúdo e tamanho da requisição
            comprimento_informacao = int(self.headers['Content-Length'])
            dados_adicionados = self.rfile.read(comprimento_informacao)
            # Recupera informações do POST
            dados_livro = json.loads(dados_adicionados)
            # Cria livro
            novo_livro = {
                'id': contador_id_livro,
                'titulo': dados_livro.get('titulo'),
                'genero': dados_livro.get('genero', 'desconhecido'),
                'ano': dados_livro.get('ano', 'desconhecido'),
                'id_autor': dados_livro.get('id_autor', None) 
            }

            # Verifica se o título do livro está na requisição
            if not novo_livro['titulo']:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"message": "O título é obrigatório"}).encode())
                return
            
            # Adiciona a associação entre autor e livro caso id_autor seja informado
            id_autor = dados_livro.get('id_autor')
            if id_autor:
                if id_autor not in associacoes:
                    associacoes[id_autor] = set()
                associacoes[id_autor].add(id_livro)

            
            livros[contador_id_livro] = novo_livro
            contador_id_livro += 1
            self.definir_cabecalho(201)
            self.wfile.write(json.dumps(novo_livro).encode())

        # POST para associar livro ao autor (rota: /autores/{id}/livros/{id_livro})
        elif len(caminho) == 5 and caminho[1] == 'autores' and caminho[3] == 'livros':
            try:
                id_autor = int(caminho[2])
                id_livro = int(caminho[4])

                # Verificações
                if id_autor in autores and id_livro in livros:
                    if id_autor not in autores:
                        self.definir_cabecalho(404)
                        self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
                        return
                    if id_livro in associacoes[id_autor]:
                        self.definir_cabecalho(409)  # 409 significa conflito
                        self.wfile.write(json.dumps({'message': 'A associação já existe'}).encode())
                        return
                    if id_autor not in associacoes:
                        associacoes[id_autor] = set()
                    associacoes[id_autor].add(id_livro)

                    # Adicionar id do autor nas informações do livro
                    livro = livros[id_livro]
                    livro['id_autor'] = id_autor

                    self.definir_cabecalho(201)
                    self.wfile.write(json.dumps({'message': 'Associação criada com sucesso'}).encode())
                else: 
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor ou livro não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função GET (Recupera todos os autores ou todos os livros)
    def do_GET(self):
        caminho = self.caminho_URL()  

        # Mostrar todos os autores
        if self.path == '/autores':  
            self.definir_cabecalho(200)
            self.wfile.write(json.dumps(list(autores.values())).encode())
        # Mostrar autor específico pelo ID    
        elif len(caminho) == 3 and caminho[1] == 'autores':
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

        # Mostrar todos os livros
        elif self.path == '/livros':
            self.definir_cabecalho(200)
            self.wfile.write(json.dumps(list(livros.values())).encode())
        # Mostrando livro específico pelo ID
        elif len(caminho) == 3 and caminho[1] == 'livros':
            try:
                id_livro = int(caminho[2])
                livro = livros.get(id_livro)
                if livro:
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(livro).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({"message": "Livro não encontrado"}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"message": "ID inválido"}).encode())

        # Mostrando todos os livros de um ator (rota: /autores/{id}/livros)
        elif len(caminho) == 4 and caminho[1] == 'autores' and caminho[3] == 'livros':
            try:
                id_autor = int(caminho[2])
                # Verifica se o autor possui associações
                if id_autor in associacoes:
                    # Recupera todos os livros associados ao autor
                    livros_do_autor = associacoes[id_autor]
                    livros_associados = [livros[livro_id] for livro_id in livros_do_autor if livro_id in livros]
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(livros_associados).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado ou não possui livros associados'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função PUT (atualiza um autor ou um livro que ja existam)
    def do_PUT(self):
        caminho = self.caminho_URL()

        # PUT dos autores
        if len(caminho) == 3 and caminho[1] == 'autores':
            try:
                id_autor = int(caminho[2])
                if id_autor in autores:
                    # Recupera conteúdo e tamanho da requisição
                    comprimento_informacao = int(self.headers['Content-Length'])
                    # Recupera informações do PUT
                    put_data_autores = self.rfile.read(comprimento_informacao)
                    dados_adicionados_autores = json.loads(put_data_autores)

                    # Atualiza informações do autor
                    autores[id_autor].update(dados_adicionados_autores)
                    autor = autores[id_autor]
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(autor).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())
        
        # PUT dos livros
        elif len(caminho) == 3 and caminho[1] == 'livros':
            try:
                id_livro = int(caminho[2])
                if id_livro in livros:
                    # Recupera conteúdo e tamanho da requisição
                    comprimento_informacao = int(self.headers['Content-Length'])
                    # Recupera informações do PUT
                    put_data_livros = self.rfile.read(comprimento_informacao)
                    dados_adicionados_livros = json.loads(put_data_livros)
        
                    # Atualiza informações do livro
                    livros[id_livro].update(dados_adicionados_livros)
                    livro = livros[id_livro]
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(livro).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'livro não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"message": "ID inválido"}).encode())

        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({'message': 'Rota não encontrada'}).encode())

    # Função DELETE (Deleta um autor ou um livro)
    def do_DELETE(self):
        caminho = self.caminho_URL()

        #Delete de autores
        if len(caminho) == 3 and caminho[1] == 'autores':  
            try:
                id_autor = int(caminho[2]) 
                if id_autor in autores:
                    # Deleta um autor
                    del autores[id_autor]
                    # Deleta o autor das associações
                    if id_autor in associacoes:
                        del associacoes[id_autor]
                    # Remove todas as referências ao autor em todos os livros
                    for livro in livros.value():
                        if livro.get('id_autor') == id_autor:
                            livro['id_autor'] = ''
                    self.definir_cabecalho(204)
                    self.wfile.write(json.dumps({'message': 'Autor removido'}).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Autor não encontrado'}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({'message': 'ID inválido'}).encode())

        # Delete de livros
        elif len(caminho) == 3 and caminho[1] == 'livros':
            try: 
                id_livro = int(caminho[2])
                if id_livro in livros:
                    # Deleta um livro
                    del livros[id_livro]
                    # Remove o livro de todas as associações
                    for autor_id in associacoes:
                        if id_livro in associacoes[autor_id]:
                            associacoes[autor_id].remove(id_livro)
                            # Se vazio, remove as assosicações
                            if not associacoes[autor_id]:
                                del associacoes[autor_id]
                    self.definir_cabecalho(204)
                    self.wfile.write(json.dumps({'message': 'Livro removido'}).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({"message": "Livro não encontrado"}).encode())
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"message": "ID inválido"}).encode())

        # Delete de associações (/authors/{id}/books/{book_id})
        elif len(caminho) == 5 and caminho[1] == 'autores' and caminho[3] == 'livros':
            try:
                autor_id = int(caminho[2])
                livro_id = int(caminho[4])
                
                if autor_id in associacoes and livro_id in associacoes[autor_id]:
                    # Remove o livro do autor
                    associacoes[autor_id].remove(livro_id)
                    # Se a coleção está vazia, a mesma é deletada
                    if not associacoes[autor_id]:
                        del associacoes[autor_id]
                    # Retira o id do autor das informações do livro
                    if livro_id in livros:
                        livro = livros[livro_id]
                        livro['id_autor'] = ''
                    # Retorno
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps({'message': 'Associação removida com sucesso'}).encode())
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({'message': 'Associação não encontrada'}).encode())
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