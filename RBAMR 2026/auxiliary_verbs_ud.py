# -*- coding: utf-8 -*-
"""
Adaptado de srl_auxiliary_verbs.py (Hartmann, 2014) para UD/AMR.
Mantém as regras originais de aspecto, modalidade e tempo.
"""
from typing import List, Dict

# Tabela original de regras SRL adaptada para verificação de vizinhança
# Formato: (lemma_auxiliar, preposicao_ou_vazio, papel_no_amr)
RULES = [
    ('acabar', '', 'argm-asp'), ('acabar', 'de', 'argm-asp'), ('acabar', 'por', 'argm-asp'),
    ('andar', '', 'argm-asp'), ('cessar', 'de', 'argm-asp'), ('chegar', 'a', 'argm-asp'),
    ('começar', 'a', 'argm-asp'), ('começar', 'por', 'argm-asp'), ('continuar', 'a', 'argm-asp'),
    ('correr', 'a', 'argm-asp'), ('costumar', '', 'argm-asp'), ('dar', 'de', 'argm-asp'),
    ('deixar', 'de', 'argm-asp'), ('desatar', 'a', 'argm-asp'), ('dever', '', 'argm-mod'),
    ('estar', 'para', 'argm-asp'), ('estar', '', 'argm-asp'), ('estar', 'por', 'argm-asp'),
    ('ficar', '', 'argm-asp'), ('ficar', 'sem', 'argm-asp'), ('ficar', 'de', 'argm-mod'),
    ('haver', 'de', 'argm-mod'), ('haver', 'que', 'argm-mod'), ('haver', '', 'argm-tml'),
    ('hesitar', 'em', 'argm-asp'), ('ir', '', 'argm-asp'), ('ir', '', 'argm-tml'),
    ('ousar', '', 'argm-asp'), ('parar', 'de', 'argm-asp'), ('passar', 'a', 'argm-asp'),
    ('permanecer', '', 'argm-asp'), ('poder', '', 'argm-mod'), ('recomeçar', 'a', 'argm-asp'),
    ('sair', '', 'argm-asp'), ('seguir', '', 'argm-asp'), ('ser', '', 'argm-pas'),
    ('ter', 'de', 'argm-mod'), ('ter', 'que', 'argm-mod'), ('ter', '', 'argm-tml'),
    ('terminar', '', 'argm-asp'), ('tornar', 'a', 'argm-asp'), ('vir', '', 'argm-asp'),
    ('vir', 'a', 'argm-asp'), ('viver', '', 'argm-asp'), ('voltar', 'a', 'argm-asp')
]

def is_auxiliary(token: Dict, sent: List[Dict]) -> bool:
    """Critério híbrido: Etiqueta UD + Regras Hartmann."""
    # 1. Se o parser UD já marcou como AUX, aceitamos
    if token.get("upos") == "AUX":
        return True

    # 2. Busca na tabela de regras (V + Prep + V)
    current_idx = -1
    for i, t in enumerate(sent):
        if t['id'] == token['id']:
            current_idx = i
            break

    if current_idx != -1:
        lemma = token['lemma'].lower()
        for aux_l, prep, role in RULES:
            if lemma == aux_l:
                # Caso: Verbo Auxiliar + Próximo Token
                if current_idx + 1 < len(sent):
                    next_t = sent[current_idx + 1]
                    # Se a regra não pede preposição e o próximo é um verbo
                    if not prep and next_t.get('upos') in ['VERB', 'AUX']:
                        return True
                    # Se a regra pede preposição e ela está presente
                    if prep and next_t['lemma'].lower() == prep:
                        return True
    return False

def normalize_aux_verbs(sent: List[Dict]):
    """Interface de integração: marca o token para o ModernAMRParser."""
    for tok in sent:
        if is_auxiliary(tok, sent):
            if "feats" not in tok or not isinstance(tok["feats"], dict):
                tok["feats"] = {}
            tok["feats"]["IsAuxiliary"] = "Yes"
    return sent