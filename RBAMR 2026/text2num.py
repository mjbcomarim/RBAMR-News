# -*- coding: utf-8 -*-
import re

class TextToNumber:
    def __init__(self):
        self.ordinal = {
            'primeiro': 1, 'segundo': 2, 'terceiro': 3, 'quarto': 4,
            'quinto': 5, 'sexto': 6, 'setimo': 7, 'oitavo': 8,
            'nono': 9, 'decimo': 10
        }
        self.small = {
            'zero': 0, 'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 
            'quatro': 4, 'cinco': 5, 'seis': 6, 'sete': 7, 'oito': 8, 
            'nove': 9, 'dez': 10, 'onze': 11, 'doze': 12, 'treze': 13, 
            'quatorze': 14, 'catorze': 14, 'quinze': 15, 'dezesseis': 16, 
            'dezessete': 17, 'dezoito': 18, 'dezenove': 19, 'vinte': 20, 
            'trinta': 30, 'quarenta': 40, 'cinquenta': 50, 'sessenta': 60, 
            'setenta': 70, 'oitenta': 80, 'noventa': 90
        }
        self.magnitude = {
            'mil': 1000, 'milhão': 1000000, 'bilhão': 1000000000
        }

    def convert(self, text):
        """Converte string numérica para int ou retorna o texto original."""
        if not text: return text
        word = text.lower()
        
        if word in self.ordinal:
            return self.ordinal[word]
        
        parts = re.split(r"[\s-]+", word)
        n, g = 0, 0
        for w in parts:
            if w == 'e': continue
            x = self.small.get(w)
            if x is not None:
                g += x
            elif w == "cem" and g != 0:
                g *= 100
            else:
                x = self.magnitude.get(w)
                if x is not None:
                    n += g * x
                    g = 0
                else:
                    return text
        return n + g