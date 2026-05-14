import json
import os
from conllu import parse

# =========================================================
# CONFIGURAÇÕES
# =========================================================

ARQUIVO_INPUT = "input.conllu"
ARQUIVO_OUTPUT = "output_srl.conllu"
ARQUIVO_JSON_VB = "verbo_brasil_db.json"

# =========================================================
# CARREGAR VERBO-BRASIL
# =========================================================

def carregar_verbo_brasil():

    if not os.path.exists(ARQUIVO_JSON_VB):

        print(f"Erro: {ARQUIVO_JSON_VB} não encontrado.")
        return None

    with open(
        ARQUIVO_JSON_VB,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

# =========================================================
# LISTAS SEMÂNTICAS
# =========================================================

TEMPORAIS = {
    "já", "agora", "hoje",
    "amanhã", "ontem",
    "nunca", "sempre"
}

LOCATIVOS = {
    "aqui", "ali", "lá",
    "acima", "abaixo",
    "fora", "dentro"
}

PREPOSICOES = {
    "com", "para", "por",
    "de", "em", "sobre",
    "contra", "entre",
    "até"
}

MOTION_WORDS = {
    "movimento",
    "trajeto",
    "caminho",
    "origem",
    "destino",
    "ponto final",
    "ponto inicial",
    "deslocamento"
}

MENTAL_WORDS = {
    "experiencer",
    "experienciador",
    "sentimento",
    "emoção",
    "pensador",
    "percepção",
    "surpresa"
}

COMM_WORDS = {
    "falante",
    "ouvinte",
    "mensagem",
    "informação",
    "comunicação"
}

CAUSATIVE_WORDS = {
    "causa",
    "causador",
    "causer",
    "agente causador"
}

REFLEXIVE_WORDS = {
    "pronome reflexivo",
    "-se"
}

# =========================================================
# EXTRAÇÃO DE FEATURES
# =========================================================

def extrair_features(verbo, filhos, tokens):

    features = {
        "lemma": verbo["lemma"].lower(),
        "subject": None,
        "object": None,
        "iobj": None,
        "preps": [],
        "advs": [],
        "reflexive": False,
        "passive": False,
        "xcomp": False,
        "ccomp": False
    }

    for child in filhos:

        dep = child["deprel"]
        lemma = child["lemma"].lower()

        # -------------------------------------------------
        # sujeito
        # -------------------------------------------------

        if dep in ["nsubj", "nsubj:pass"]:

            features["subject"] = lemma

        # -------------------------------------------------
        # objeto direto
        # -------------------------------------------------

        elif dep == "obj":

            features["object"] = lemma

        # -------------------------------------------------
        # objeto indireto
        # -------------------------------------------------

        elif dep == "iobj":

            features["iobj"] = lemma

        # -------------------------------------------------
        # oblíquos
        # -------------------------------------------------

        elif dep.startswith("obl"):

            features["preps"].append(lemma)

        # -------------------------------------------------
        # advérbios
        # -------------------------------------------------

        elif dep == "advmod":

            features["advs"].append(lemma)

        # -------------------------------------------------
        # reflexividade
        # -------------------------------------------------

        elif dep.startswith("expl"):

            if lemma == "se":

                features["reflexive"] = True

        # -------------------------------------------------
        # passiva
        # -------------------------------------------------

        elif dep == "aux:pass":

            features["passive"] = True

        # -------------------------------------------------
        # complementos
        # -------------------------------------------------

        elif dep == "xcomp":

            features["xcomp"] = True

        elif dep == "ccomp":

            features["ccomp"] = True

    return features

# =========================================================
# TEXTO DO FRAME
# =========================================================

def frame_texto(frame):

    return json.dumps(
        frame,
        ensure_ascii=False
    ).lower()

# =========================================================
# HEURÍSTICAS
# =========================================================

def frame_reflexivo(frame):

    texto = frame_texto(frame)

    return any(
        palavra in texto
        for palavra in REFLEXIVE_WORDS
    )

def detectar_preps_frame(frame):

    texto = frame_texto(frame)

    achadas = []

    for prep in PREPOSICOES:

        if f"({prep}" in texto or f" {prep} " in texto:

            achadas.append(prep)

    return achadas

def frame_movimento(frame):

    texto = frame_texto(frame)

    return any(
        palavra in texto
        for palavra in MOTION_WORDS
    )

def frame_mental(frame):

    texto = frame_texto(frame)

    return any(
        palavra in texto
        for palavra in MENTAL_WORDS
    )

def frame_comunicacao(frame):

    texto = frame_texto(frame)

    return any(
        palavra in texto
        for palavra in COMM_WORDS
    )

def frame_causativo(frame):

    texto = frame_texto(frame)

    return any(
        palavra in texto
        for palavra in CAUSATIVE_WORDS
    )

# =========================================================
# PONTUAÇÃO DOS FRAMES
# =========================================================

def pontuar_frame(frame, features):

    score = 0

    texto = frame_texto(frame)

    # -------------------------------------------------
    # reflexivo
    # -------------------------------------------------

    if features["reflexive"]:

        if frame_reflexivo(frame):

            score += 10

    # -------------------------------------------------
    # preposições
    # -------------------------------------------------

    preps_frame = detectar_preps_frame(frame)

    for prep in features["preps"]:

        if prep in preps_frame:

            score += 5

    # -------------------------------------------------
    # movimento
    # -------------------------------------------------

    if frame_movimento(frame):

        score += 3

    # -------------------------------------------------
    # mental
    # -------------------------------------------------

    if frame_mental(frame):

        score += 3

    # -------------------------------------------------
    # comunicação
    # -------------------------------------------------

    if frame_comunicacao(frame):

        score += 3

    # -------------------------------------------------
    # causativo
    # -------------------------------------------------

    if frame_causativo(frame):

        score += 2

    # -------------------------------------------------
    # xcomp
    # -------------------------------------------------

    if features["xcomp"]:

        if "oração" in texto:

            score += 3

    # -------------------------------------------------
    # ccomp
    # -------------------------------------------------

    if features["ccomp"]:

        if "conteúdo" in texto:

            score += 3

    # -------------------------------------------------
    # passiva
    # -------------------------------------------------

    if features["passive"]:

        score += 1

    return score

# =========================================================
# ESCOLHA DO ROLESET
# =========================================================

def escolher_roleset(lema, frames, features):

    if len(frames) == 1:

        return frames[0]

    melhor_frame = None
    melhor_score = -1

    for frame in frames:

        score = pontuar_frame(
            frame,
            features
        )

        if score > melhor_score:

            melhor_score = score
            melhor_frame = frame

    # fallback
    if melhor_frame is None:

        return {
            "roleset": f"{lema}.01",
            "args": {}
        }

    return melhor_frame

# =========================================================
# IDENTIFICAR SUJEITO EXTENSO
# =========================================================

def identificar_sujeito_extenso(
    verbo_id,
    tokens,
    filhos_map
):

    filhos = filhos_map.get(
        verbo_id,
        []
    )

    # -------------------------------------------------
    # sujeito direto
    # -------------------------------------------------

    for child in filhos:

        if child["deprel"] in [
            "nsubj",
            "nsubj:pass"
        ]:

            return child

    # -------------------------------------------------
    # herança
    # -------------------------------------------------

    verbo = tokens[verbo_id]

    if verbo["deprel"] in [
        "xcomp",
        "ccomp",
        "conj"
    ]:

        head = verbo["head"]

        if head in tokens:

            return identificar_sujeito_extenso(
                head,
                tokens,
                filhos_map
            )

    return None

# =========================================================
# IDENTIFICAÇÃO DOS ARGUMENTOS
# =========================================================

def identificar_argumentos(
    verbo,
    filhos,
    tokens,
    filhos_map,
    arg_defs,
    passive
):

    resultados = []

    # -------------------------------------------------
    # sujeito
    # -------------------------------------------------

    sujeito = identificar_sujeito_extenso(
        verbo["id"],
        tokens,
        filhos_map
    )

    if sujeito:

        papel = "Arg1" if passive else "Arg0"

        desc = arg_defs.get(
            papel,
            "Sujeito"
        )

        resultados.append({
            "papel": papel,
            "texto": sujeito["form"],
            "descricao": desc,
            "dep": sujeito["deprel"],
            "token_id": sujeito["id"]
        })

    # -------------------------------------------------
    # demais filhos
    # -------------------------------------------------

    for child in filhos:

        dep = child["deprel"]
        lemma = child["lemma"].lower()

        papel = None

        # evitar duplicação do sujeito
        if dep in ["nsubj", "nsubj:pass"]:

            continue

        # -------------------------------------------------
        # objetos
        # -------------------------------------------------

        if dep == "obj":

            papel = "Arg1"

        elif dep == "iobj":

            papel = "Arg2"

        # -------------------------------------------------
        # complementos
        # -------------------------------------------------

        elif dep == "xcomp":

            papel = "Arg1"

        elif dep == "ccomp":

            papel = "Arg1"

        # -------------------------------------------------
        # adjuntos
        # -------------------------------------------------

        elif dep == "advmod":

            if lemma in TEMPORAIS:

                papel = "ArgM-TMP"

            else:

                papel = "ArgM-MNR"

        elif dep.startswith("obl"):

            papel = "ArgM-LOC"

        elif dep == "advcl":

            papel = "ArgM-ADV"

        # -------------------------------------------------
        # salvar argumento
        # -------------------------------------------------

        if papel:

            desc = arg_defs.get(
                papel.split("-")[0],
                "Adjunto"
            )

            resultados.append({
                "papel": papel,
                "texto": child["form"],
                "descricao": desc,
                "dep": dep,
                "token_id": child["id"]
            })

    return resultados

# =========================================================
# MAPA SRL
# =========================================================

def montar_srl_map(argumentos, pred_id):

    srl_map = {}

    for arg in argumentos:

        tok_id = arg["token_id"]

        label = f"{arg['papel']}:{pred_id}"

        if tok_id not in srl_map:

            srl_map[tok_id] = []

        srl_map[tok_id].append(label)

    return srl_map

# =========================================================
# EXECUÇÃO PRINCIPAL
# =========================================================

def executar_srl_conllu(db):

    if not os.path.exists(ARQUIVO_INPUT):

        print(f"Erro: {ARQUIVO_INPUT} não encontrado.")
        return

    with open(
        ARQUIVO_INPUT,
        "r",
        encoding="utf-8"
    ) as f:

        sentencas = parse(f.read())

    print(
        f"\nProcessando "
        f"{len(sentencas)} sentenças...\n"
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    with open(
        ARQUIVO_OUTPUT,
        "w",
        encoding="utf-8"
    ) as out:

        # =================================================
        # SENTENÇAS
        # =================================================

        for sent_id, sent in enumerate(
            sentencas,
            start=1
        ):

            texto = sent.metadata.get(
                "text",
                ""
            )

            print("=" * 70)
            print(f"FRASE: {texto}")

            # -------------------------------------------------
            # metadados
            # -------------------------------------------------

            out.write(f"# sent_id = {sent_id}\n")
            out.write(f"# text = {texto}\n")

            # -------------------------------------------------
            # indexação
            # -------------------------------------------------

            tokens = {
                tok["id"]: tok
                for tok in sent
                if isinstance(tok["id"], int)
            }

            # -------------------------------------------------
            # mapa de filhos
            # -------------------------------------------------

            filhos_map = {
                i: []
                for i in tokens
            }

            for tok in tokens.values():

                head = tok["head"]

                if head in filhos_map:

                    filhos_map[head].append(tok)

            # -------------------------------------------------
            # estruturas SRL
            # -------------------------------------------------

            srl_labels = {}
            rolesets = {}

            # =================================================
            # VERBOS
            # =================================================

            for tok in tokens.values():

                if tok["upos"] != "VERB":

                    continue

                lema = tok["lemma"].lower()

                filhos = filhos_map[tok["id"]]

                # -------------------------------------------------
                # features
                # -------------------------------------------------

                features = extrair_features(
                    tok,
                    filhos,
                    tokens
                )

                # -------------------------------------------------
                # frames VerboBrasil
                # -------------------------------------------------

                frames_vb = db.get(lema)

                if not frames_vb:

                    frame_escolhido = {
                        "roleset": f"{lema}.01",
                        "args": {}
                    }

                else:

                    frame_escolhido = escolher_roleset(
                        lema,
                        frames_vb,
                        features
                    )

                roleset = frame_escolhido["roleset"]

                arg_defs = frame_escolhido.get(
                    "args",
                    {}
                )

                rolesets[tok["id"]] = roleset

                # -------------------------------------------------
                # argumentos
                # -------------------------------------------------

                argumentos = identificar_argumentos(
                    tok,
                    filhos,
                    tokens,
                    filhos_map,
                    arg_defs,
                    features["passive"]
                )

                # -------------------------------------------------
                # mapa SRL
                # -------------------------------------------------

                mapa_local = montar_srl_map(
                    argumentos,
                    tok["id"]
                )

                for tok_id, labels in mapa_local.items():

                    if tok_id not in srl_labels:

                        srl_labels[tok_id] = []

                    srl_labels[tok_id].extend(labels)

                # -------------------------------------------------
                # debug
                # -------------------------------------------------

                print("\n" + "-" * 50)
                print(f"VERBO: {tok['form']}")
                print(f"ROLESET: {roleset}")

                for arg in argumentos:

                    print(
                        f"   [{arg['papel']}] "
                        f"{arg['texto']}"
                    )

            # =================================================
            # ESCREVER CONLLU FINAL
            # =================================================

            for tok in sent:

                if not isinstance(tok["id"], int):

                    continue

                tok_id = tok["id"]

                # -------------------------------------------------
                # coluna 9 -> roleset
                # -------------------------------------------------

                col9 = rolesets.get(
                    tok_id,
                    "_"
                )

                # -------------------------------------------------
                # coluna 10 -> SRL
                # -------------------------------------------------

                labels = srl_labels.get(
                    tok_id,
                    []
                )

                col10 = (
                    "|".join(sorted(set(labels)))
                    if labels
                    else "_"
                )

                # -------------------------------------------------
                # FEATS
                # -------------------------------------------------

                feats_str = (
                    "|".join(
                        f"{k}={v}"
                        for k, v in tok["feats"].items()
                    )
                    if tok.get("feats")
                    else "_"
                )

                # -------------------------------------------------
                # linha final
                # -------------------------------------------------

                linha = [

                    str(tok["id"]),

                    str(tok.get("form") or "_"),

                    str(tok.get("lemma") or "_"),

                    str(tok.get("upos") or "_"),

                    str(tok.get("xpos") or "_"),

                    feats_str,

                    str(
                        tok.get("head")
                        if tok.get("head") is not None
                        else 0
                    ),

                    str(tok.get("deprel") or "_"),

                    str(col9 or "_"),

                    str(col10 or "_")
                ]

                out.write(
                    "\t".join(linha) + "\n"
                )

            out.write("\n")

    print(
        f"\nArquivo gerado com sucesso: "
        f"{ARQUIVO_OUTPUT}"
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    db = carregar_verbo_brasil()

    if db is not None:

        executar_srl_conllu(db)