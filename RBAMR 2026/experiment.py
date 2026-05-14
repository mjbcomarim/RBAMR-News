# -*- coding: utf-8 -*-
import os
import sys
import copy
import importlib
from datetime import datetime

# Ajuste de ambiente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

import modern_amr_parser

# Lista atualizada para cobrir todas as linhas da tabela de ablação
SEMANTIC_RULES = [
    # Regras de Semântica/Lógica
    "NEGATION", "MODAL_OBLIGATE", "MODAL_POSSIBLE", "PASSIVE_VOICE",
    "SUBJECT_INSERTION", "NER", "CONTRAST", "QUESTION", "ORDINAL",
    
    # Regras de Estrutura de Argumentos (UD -> AMR)
    "NSUBJ", "OBJ", "NMOD", "XCOMP", "NSUBJ_PASS", "IOBJ",
    
    # Regras de Modificadores e Outros
    "AMOD", "ADVMOD", "NUMMOD", "CC", "CONJ", "STOPWORD", "POSSE", "COPULA"
]

OUTPUT_DIR = "experimento_semantico"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# RENDERIZADOR (IDÊNTICO AO SEU RUN_PARSER)
# ==========================================
def render_amr(nodes, current_var, visited, depth=0):
    if current_var == '-': return "-"
    if isinstance(current_var, str) and current_var.startswith('"'): return current_var
    if current_var not in nodes: return str(current_var)
    
    info = nodes[current_var]
    indent = "    " * (depth + 1)
    amr_str = f"({info['var']} / {info['concept']}"
    
    for role, target in info.get('edges', []):
        val = render_amr(nodes, target, visited, depth + 1)
        amr_str += f"\n{indent}{role} {val}"
            
    return amr_str + ")"

# ==========================================
# FLUXO DO EXPERIMENTO
# ==========================================
def run_step(data_original, rule_to_disable=None):
    # Força reinicialização do parser para limpar estados
    importlib.reload(modern_amr_parser)
    parser = modern_amr_parser.ModernAMRParser()
    
    if rule_to_disable:
        parser.disabled_rules = {rule_to_disable}
        filename = f"ablation_{rule_to_disable.lower()}.txt"
    else:
        parser.disabled_rules = set()
        filename = "00_baseline_completo.txt"

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Gerando: {filename}")
    
    path = os.path.join(OUTPUT_DIR, filename)
    
    with open(path, 'w', encoding='utf-8') as f_out:
        for sent in data_original:
            # Deepcopy para garantir integridade dos dados originais
            sent_copy = copy.deepcopy(sent)
            
            # Execução do parser
            res_list = parser.execute([sent_copy])

            if not res_list:
                continue
            
            data_res = res_list[0]
            nodes = data_res['nodes']
            root_var = data_res['root']
            
            # Recuperação de texto via metadata
            try:
                tokens_str = sent.metadata.get('text', '')
            except:
                tokens_str = " ".join([t.get('form', '') for t in sent])

            f_out.write(f"# ::tok {tokens_str}\n")

            if root_var and root_var in nodes:
                f_out.write(render_amr(nodes, root_var, set()) + "\n\n")
            elif nodes:
                fallback = list(nodes.keys())[0]
                f_out.write(render_amr(nodes, fallback, set()) + "\n\n")

def main():
    try:
        from conllu import parse
        with open('entrada.conllu', 'r', encoding='utf-8') as f:
            data = parse(f.read())
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return

    # Executa Baseline (Sistema completo)
    run_step(data)

    # Executa Ablações (Uma por uma)
    for rule in SEMANTIC_RULES:
        run_step(data, rule)

    print(f"\nSucesso! Arquivos gerados em: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()