# -*- coding: utf-8 -*-

def get_named_entity(resources, form):
    if not form: return "thing"
    name = form.lower()

    mapping = [
        ('cities', 'city'), ('countries', 'country'),
        ('states', 'state'), ('continents', 'continent')
    ]

    for key, category in mapping:
        if name in resources.get(key, set()):
            return category

    # Se começar com maiúscula, no AMR assume-se 'person' por padrão
    if form[0].isupper():
        return "person"
    
    return "thing"