# -*- coding: utf-8 -*-

class SubjectInsertor:
    def __init__(self):
        self.IMPERSONAL = ['haver', 'existir', 'chover', 'nevar']
        # Mapeamento
        self.PRONOUN_MAP = {
            "Number=Sing|Person=1": "eu",
            "Number=Plur|Person=1": "nós",
            "Number=Sing|Person=3": "ele",
            "Number=Plur|Person=3": "eles"
        }

    def get_virtual_node(self, token):
        """Retorna o lemma do pronome baseado na morfologia do verbo."""
        if token['upos'] != 'VERB' or token['lemma'] in self.IMPERSONAL:
            return None
        
        feats = token.get('feats', {})
        if not feats: return None
        
        # Tenta encontrar a combinação de Pessoa e Número
        p = feats.get('Person')
        n = feats.get('Number')
        key = f"Number={n}|Person={p}"
        
        return self.PRONOUN_MAP.get(key)