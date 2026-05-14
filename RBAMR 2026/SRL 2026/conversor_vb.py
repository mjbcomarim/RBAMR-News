import os
import json
import re
from bs4 import BeautifulSoup

# --- CONFIGURAÇÃO ---
PASTA_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Verbo-Brasil')
ARQUIVO_SAIDA = 'verbo_brasil_db.json'

def extrair_com_regex(html_text):
    """
    Procura padrões de ArgX ou Argm no texto bruto do HTML
    """
    # Procura por "ArgX: descrição" ou "Argm-xxx: descrição"
    padrao = r"<b>(Arg[0-9a-z-]+)<\/b>:\s*<i>([^<]+)<\/i>"
    matches = re.findall(padrao, html_text, re.IGNORECASE)
    
    arg_map = {}
    for arg_id, descricao in matches:
        # Limpa o texto da descrição (remove lixo de encoding como 'advers?rio')
        desc_limpa = descricao.replace('?', 'a').strip() 
        arg_map[arg_id] = desc_limpa
        
    return arg_map

def converter_verbo_brasil_final():
    banco_verbos = {}
    
    if not os.path.exists(PASTA_HTML):
        print(f"Erro: Pasta {PASTA_HTML} não encontrada.")
        return

    arquivos = [f for f in os.listdir(PASTA_HTML) if f.endswith('.html')]
    print(f"A processar {len(arquivos)} ficheiros...")

    for nome_arquivo in arquivos:
        caminho = os.path.join(PASTA_HTML, nome_arquivo)
        
        # Usamos 'latin-1' ou 'utf-8' com ignore para evitar erros de caracteres especiais do Verbo-Brasil
        with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
            conteudo_completo = f.read()
            soup = BeautifulSoup(conteudo_completo, 'html.parser')
            
            # 1. Extração do Lema (Verbo)
            tag_verbo = soup.find("font", {"color": "red"})
            if not tag_verbo:
                # Tentativa secundária caso a tag red não exista
                tag_verbo = soup.find("h2")
            
            if not tag_verbo:
                continue
                
            verbo_lema = tag_verbo.text.replace("Predicate:", "").strip().lower()

            # 2. Dividir o HTML por Rolesets
            # O Verbo-Brasil separa os sentidos por "Roleset id:"
            partes_roleset = re.split(r'Roleset id:', conteudo_completo)
            
            rolesets_extraidos = []
            
            # A primeira parte antes do primeiro Roleset id é o cabeçalho, ignoramos
            for i, parte in enumerate(partes_roleset[1:], 1):
                # Captura os argumentos dentro desta parte específica do texto
                args = extrair_com_regex(parte)
                
                if args:
                    rolesets_extraidos.append({
                        "roleset": f"{verbo_lema}.{i:02d}",
                        "args": args
                    })

            if rolesets_extraidos:
                banco_verbos[verbo_lema] = rolesets_extraidos
                print(f"✓ {verbo_lema} guardado.")

    # Gravação do JSON
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as j:
        json.dump(banco_verbos, j, indent=4, ensure_ascii=False)
    
    print(f"\nConcluído! Arquivo '{ARQUIVO_SAIDA}' criado com {len(banco_verbos)} verbos.")

if __name__ == "__main__":
    converter_verbo_brasil_final()
