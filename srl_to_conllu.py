#import spacy
import json
import os

# --- CONFIGURAÇÕES ---
INPUT_FILE = 'TLP.txt'
OUTPUT_FILE = 'srl_processed.conllu'
VB_JSON = 'verbo_brasil_db.json'

def carregar_recursos():
    """Carrega o modelo spaCy e a base de conhecimento do Verbo-Brasil."""
    if os.path.exists(VB_JSON):
        with open(VB_JSON, 'r', encoding='utf-8') as f:
            db = json.load(f)
        print(f"Sucesso: {len(db)} verbos carregados do Verbo-Brasil.")
    else:
        print(f"Aviso: {VB_JSON} não encontrado. Usando apenas regras heurísticas.")
        db = {}

    try:
        nlp = spacy.load("pt_core_news_lg")
    except:
        print("Erro: Modelo pt_core_news_lg não encontrado.")
        return None, None
    
    return nlp, db

def identificar_sujeito_extenso(token):
    """
    Busca o núcleo do sujeito. 
    Lida com elementos implícitos subindo na árvore (coordenação e subordinadas).
    """
    # 1. Busca direta nos filhos
    for child in token.children:
        if child.dep_ in ["nsubj", "nsubj:pass"]:
            return child
    
    # 2. Se for conjunção ou subordinada (xcomp/ccomp), tenta herdar do pai (implícito)
    if token.dep_ in ["ccomp", "xcomp", "conj"]:
        return identificar_sujeito_extenso(token.head)
    
    return None

def processar_srl():
    nlp, db = carregar_recursos()
    if not nlp or not os.path.exists(INPUT_FILE):
        print(f"Erro: Verifique se {INPUT_FILE} existe.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        sentencas = [l.strip() for l in f.readlines() if l.strip()]

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for s_idx, texto in enumerate(sentencas):
            doc = nlp(texto)
            out.write(f"# sent_id = {s_idx + 1}\n")
            out.write(f"# text = {texto}\n")
            
            srl_map = {} # {token_idx: [lista_de_labels]}

            # Identifica predicados (Verbos e Auxiliares)
            predicados = [t for t in doc if t.pos_ in ["VERB", "AUX"]]

            for pred in predicados:
                p_idx = pred.i + 1
                lema = pred.lemma_.lower()
                
                # Consulta ao Verbo-Brasil (Reparando a falha do script anterior)
                # Pega o primeiro frame disponível (sentido .01)
                frames_list = db.get(lema, [])
                frame_vb = frames_list[0].get("args", {}) if frames_list else {}
                
                is_passive = any(c.dep_ == "aux:pass" for c in pred.children)
                is_copula = lema in ["ser", "estar", "ficar", "parecer"]

                # --- 1. REGRA PARA SUJEITOS (Argumentos Externos) ---
                suj = identificar_sujeito_extenso(pred)
                if suj:
                    # Lógica: Se passiva/cópula -> Arg1. 
                    # Se ativa, checa se o Verbo-Brasil prevê Arg0 (Agente).
                    if is_passive or is_copula:
                        papel = "Arg1"
                    else:
                        papel = "Arg0" if "Arg0" in frame_vb else "Arg1"
                    
                    srl_map.setdefault(suj.i + 1, []).append(f"{papel}:{p_idx}")

                # --- 2. REGRA PARA COMPLEMENTOS E ADJUNTOS ---
                for child in pred.children:
                    label = None
                    dep = child.dep_

                    # Objetos Diretos e Orações Completivas
                    if dep in ["obj", "ccomp", "xcomp"]:
                        label = "Arg1"
                    
                    # Objetos Indiretos
                    elif dep == "iobj":
                        label = "Arg2" if "Arg2" in frame_vb else "Arg1"

                    # Adjuntos (ArgM) - Implementando regras de Freitas_2024
                    elif dep in ["advmod", "obl", "advcl"]:
                        subtree_lemmas = [t.lemma_.lower() for t in child.subtree]
                        
                        # ArgM-COND (Condicional: "se", "caso")
                        if any(l in ["se", "caso"] for l in subtree_lemmas):
                            label = "ArgM-COND"
                        # ArgM-TMP (Temporal)
                        elif any(t.ent_type_ == "DATE" or t.lemma_ in ["ontem", "hoje", "já", "agora"] for t in child.subtree):
                            label = "ArgM-TMP"
                        # ArgM-LOC (Lugar)
                        elif child.ent_type_ == "LOC" or any(l in ["em", "no", "na", "onde"] for l in subtree_lemmas):
                            label = "ArgM-LOC"
                        # ArgM-CAU (Causa: "porque", "devido")
                        elif "porque" in subtree_lemmas or "visto" in subtree_lemmas:
                            label = "ArgM-CAU"
                        else:
                            label = "ArgM-ADV"

                    if label:
                        srl_map.setdefault(child.i + 1, []).append(f"{label}:{p_idx}")

            # --- ESCRITA FINAL NO FORMATO CONLL-U ---
            for token in doc:
                idx = token.i + 1
                # Coluna 9: Predicado (lema.01)
                col9 = f"{token.lemma_.lower()}.01" if token.pos_ in ["VERB", "AUX"] else "_"
                
                # Coluna 10: Argumentos SRL e Misc
                labels = srl_map.get(idx, [])
                srl_str = "|".join(sorted(list(set(labels)))) if labels else "_"
                
                misc = "SpaceAfter=No" if not token.whitespace_ else ""
                if srl_str == "_" and misc: col10 = misc
                elif srl_str != "_" and misc: col10 = f"{srl_str}|{misc}"
                else: col10 = srl_str

                line = [
                    str(idx), token.text, token.lemma_, token.pos_, "_",
                    str(token.morph) if str(token.morph) else "_",
                    str(token.head.i + 1 if token.head != token else 0),
                    token.dep_.lower(), col9, col10
                ]
                out.write("\t".join(line) + "\n")
            out.write("\n")

    print(f"Processamento concluído. Resultados salvos em: {OUTPUT_FILE}")

if __name__ == "__main__":
    processar_srl()