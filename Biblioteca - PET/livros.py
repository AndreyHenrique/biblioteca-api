from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Dicionário e contadores
livros = {}
contador_id_livro = 1
contador_id_autor = 1

class LivrosAPIREST(BaseHTTPRequestHandler):
    
    def definir_cabecalho(self, status_do_codigo = 200):
        self.send_response(status_do_codigo)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
    
    # Separando o caminho em partes    
    def caminho_URL(self):
        partes_URL = self.path.split('/')
        return partes_URL
    
    # Adicionando livros
    def do_POST(self):
        
        if self.path == '/livros':
            comprimento_informacao = int(self.headers['Content-Length'])
            print("oi")
            dados_adicionados = self.rfile.read(comprimento_informacao)
            dados = json.loads(dados_adicionados)
            
            global contador_id_livro
            novo_livro = {
                'id': contador_id_livro,
                'titulo': dados.get('titulo'),
                'genero': dados.get('genero', ''),
                'ano': dados.get('ano', ''),
                'id_autor': dados.get('id_autor', None) 
            }
            
            if not novo_livro['titulo']:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"erro": "O título é obrigatório"}).encode())
                return
            
            # Adicionando o contador (id)
            livros[contador_id_livro] = novo_livro
            contador_id_livro += 1
            self.definir_cabecalho(201)
            self.wfile.write(json.dumps(novo_livro).encode())
            
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
            
    # Listando livros
    def do_GET(self):
        partes_URL = self.caminho_URL()
        
        if len(partes_URL) == 2 and partes_URL[1] == 'livros':
            self.definir_cabecalho(200)
            self.wfile.write(json.dumps(list(livros.values())).encode())
        
        # Obtendo detalhes de um livro
        elif len(partes_URL) == 3 and partes_URL[1] == 'livros':
            try:
                id_livro = int(partes_URL[2])
                livro = livros.get(id_livro)
                if livro:
                    self.definir_cabecalho(200)
                    self.wfile.write(json.dumps(livro).encode())
                    
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
                    
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"erro": "ID inválido"}).encode())
                
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())               
            
    # atualizando um livro já existente        
    def do_PUT(self):
        partes_URL = self.caminho_URL()
        
        if len(partes_URL) == 3 and partes_URL[1] == 'livros':
            try:
                id_livro = int(partes_URL[2])
                if id_livro not in livros:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
                    return

                # Ler o conteúdo
                comprimento_informacao = int(self.headers['Content-Length'])
                dados_adicionados = self.rfile.read(comprimento_informacao)
                dados = json.loads(dados_adicionados)
                
                # Atualizar
                livro = livros[id_livro]
                livro['titulo'] = dados.get('titulo', livro['titulo'])
                livro['genero'] = dados.get('genero', livro['genero'])
                livro['ano'] = dados.get('ano', livro['ano'])
                livro['id_autor'] = dados.get('id_autor', livro['id_autor'])
                self.definir_cabecalho(200)
                self.wfile.write(json.dumps(livro).encode())
                
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"erro": "ID inválido"}).encode())
                
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
            
    # Excluindo um livro já existente
    def do_DELETE(self):
        partes_URL = self.caminho_URL()
        
        if len(partes_URL) == 3 and partes_URL[1] == 'livros':
            try: 
                id_livro = int(partes_URL[2])
                if id_livro in livros:
                    del livros[id_livro]
                    self.definir_cabecalho(204)
                    
                else:
                    self.definir_cabecalho(404)
                    self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
                    
            except ValueError:
                self.definir_cabecalho(400)
                self.wfile.write(json.dumps({"erro": "ID inválido"}).encode())
                
        else:
            self.definir_cabecalho(404)
            self.wfile.write(json.dumps({"erro": "não foi encontrado"}).encode())
            
def rodando_servidor(server_class = HTTPServer, handler_class = LivrosAPIREST, port = 8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"começando...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Servidor interrompido")
        httpd.serve_close()

if __name__ == '__main__':
    rodando_servidor()
