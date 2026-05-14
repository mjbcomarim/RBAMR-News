# -- coding: utf-8 --
import os
from subject_insertor import SubjectInsertor
from named_entity import get_named_entity
from text2num import TextToNumber


class ModernAMRParser:

    AUX_RULES = [
        ('acabar', ''), ('acabar', 'de'), ('acabar', 'por'),
        ('andar', ''),
        ('cessar', 'de'), ('chegar', 'a'),
        ('começar', 'a'), ('começar', 'por'),
        ('continuar', 'a'), ('correr', 'a'),
        ('costumar', ''), ('dar', 'de'),
        ('deixar', 'de'), ('desatar', 'a'),
        ('dever', ''), ('estar', 'para'),
        ('estar', ''), ('estar', 'por'),
        ('ficar', ''), ('ficar', 'sem'),
        ('ficar', 'de'), ('haver', 'de'),
        ('haver', 'que'), ('haver', ''),
        ('hesitar', 'em'), ('ir', ''),
        ('ousar', ''), ('parar', 'de'),
        ('passar', 'a'), ('permanecer', ''),
        ('poder', ''), ('recomeçar', 'a'),
        ('sair', ''), ('seguir', ''),
        ('ser', ''), ('ter', 'de'),
        ('ter', 'que'), ('ter', ''),
        ('terminar', ''), ('tornar', 'a'),
        ('vir', ''), ('vir', 'a'),
        ('viver', ''), ('voltar', 'a')
    ]

    CONTRAST_WORDS = {
        'mas', 'porém', 'contudo',
        'todavia', 'entretanto'
    }

    QUESTION_WORDS = {
        'quem', 'que', 'o que',
        'qual', 'quando', 'onde',
        'como', 'por que'
    }

    STOPWORDS = {
        'o', 'a', 'os', 'as',
        'um', 'uma', 'uns', 'umas',
        'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas',
        'por', 'para', 'com', 'sem',
        'sobre', 'entre'
    }

    # =========================
    # FEATURE SWITCH (ABLATION)
    # =========================
    def __init__(self, utils_path='utils'):
        self.utils_path = utils_path
        self.t2n = TextToNumber()
        self.sub_ins = SubjectInsertor()

        self.resources = self._load_all_resources()

        self.disabled_rules = set()

        self.ud_to_amr = {
            'nsubj': ':ARG0',
            'nsubj:pass': ':ARG1',
            'obj': ':ARG1',
            'iobj': ':ARG2',
            'nmod': ':ARG1',
            'amod': ':mod',
            'nummod': ':quant',
            'advmod': ':mod',
            'xcomp': ':ARG2',
            'cc': ':op',
            'conj': ':op'
        }

        self.reset_support()

    def enabled(self, rule):
        return rule not in self.disabled_rules

    def reset_support(self):

        self.rule_counts = {
            "NSUBJ": 0,
            "NSUBJ_PASS": 0,
            "OBJ": 0,
            "IOBJ": 0,
            "XCOMP": 0,
            "NMOD": 0,
            "AMOD": 0,
            "ADVMOD": 0,
            "CC": 0,
            "CONJ": 0,
            "NUMMOD": 0,
            "POSSE": 0,
            "NEGATION": 0,
            "MODAL_OBLIGATE": 0,
            "MODAL_POSSIBLE": 0,
            "PASSIVE_VOICE": 0,
            "COPULA": 0,
            "AUXILIARY": 0,
            "SUBJECT_INSERTION": 0,
            "NER": 0,
            "ORDINAL": 0,
            "STOPWORD": 0,
            "CONTRAST": 0,
            "QUESTION": 0
        }

        self.total_sentences = 0

    # =========================
    # LOAD RESOURCES
    # =========================
    def _load_all_resources(self):

        res = {}
        cats = ['cities','countries','continents','states','nationalities']

        for cat in cats:

            path = os.path.join(self.utils_path, f"{cat}.txt")

            if os.path.exists(path):
                with open(path,'r',encoding='utf-8') as f:
                    res[cat] = {
                        line.strip().lower()
                        for line in f if line.strip()
                    }
            else:
                res[cat] = set()

        return res

    # =========================
    # AUX DETECTION
    # =========================
    def is_auxiliary(self, token, sent):

        if token.get('upos') == 'AUX':
            self.rule_counts["AUXILIARY"] += 1
            return True

        lemma = token.get('lemma','').lower()

        idx = next(
            (i for i,t in enumerate(sent) if t['id']==token['id']),
            -1
        )

        if idx != -1:

            for aux_l, prep in self.AUX_RULES:

                if lemma == aux_l:

                    if idx + 1 < len(sent):
                        nxt = sent[idx+1]

                        if (
                            not prep
                            and nxt.get('upos') in ['VERB','AUX']
                        ):
                            self.rule_counts["AUXILIARY"] += 1
                            return True

                        if (
                            prep
                            and nxt.get('lemma','').lower() == prep
                        ):
                            self.rule_counts["AUXILIARY"] += 1
                            return True

        return False

    # =========================
    # MAIN PARSER
    # =========================
    def execute(self, sentences_conllu):

        results = []
        self.total_sentences += len(sentences_conllu)

        for sent in sentences_conllu:

            nodes = {}
            used_vars = {}

            is_question = any(tok.get('form')=='?' for tok in sent)

            for tok in sent:

                t_id = str(tok['id'])
                lemma = tok.get('lemma','').lower()
                upos = tok.get('upos','')

                # STOPWORDS (feature-controlled)
                if lemma in self.STOPWORDS:
                    self.rule_counts["STOPWORD"] += 1
                    if self.enabled("STOPWORD"):
                        continue

                if upos in ['PUNCT','ADP'] or lemma in ['não','nunca','nada']:
                    continue

                # ORDINAL
                if upos == 'ADJ' and lemma.endswith(('º','ª')):

                    if self.enabled("ORDINAL"):
                        self.rule_counts["ORDINAL"] += 1

                        nodes[t_id] = {
                            'var': self._generate_clean_var('ordinal', used_vars),
                            'concept': 'ordinal-entity',
                            'edges': [(':value', f'"{tok.get("form")}"')]
                        }
                        continue

                # NER
                if upos == 'PROPN':
                    self.rule_counts["NER"] += 1
                    
                    if self.enabled("NER"):
                        cat = get_named_entity(self.resources, tok.get('form'))
                        concept = cat
                        var = self._generate_clean_var(concept, used_vars)
                        n_var = self._generate_clean_var('name', used_vars)

                        nodes[t_id] = {
                            'var': var,
                            'concept': concept,
                            'edges': [(':name', f"n_{t_id}")]
                        }

                        nodes[f"n_{t_id}"] = {
                            'var': n_var,
                            'concept': 'name',
                            'edges': [(':op1', f'"{tok.get("form")}"')]
                        }
                    else:
                        concept = lemma
                        var = self._generate_clean_var(concept, used_vars)
                        nodes[t_id] = {
                            'var': var,
                            'concept': concept,
                            'edges': []
                        }
                    continue

                concept = lemma


                # MODALS
                if self.is_auxiliary(tok, sent):

                    if lemma in ['ter','haver','dever'] and self.enabled("MODAL_OBLIGATE"):
                        concept = 'obligate'
                        self.rule_counts["MODAL_OBLIGATE"] += 1

                    elif lemma == 'poder' and self.enabled("MODAL_POSSIBLE"):
                        concept = 'possible'
                        self.rule_counts["MODAL_POSSIBLE"] += 1

                # VERB NORMALIZATION
                if upos == 'VERB':

                    if lemma in ['ser','estar']:
                        self.rule_counts["COPULA"] += 1
                        concept = 'be-03'
                    elif '.' not in concept:
                        concept += '.01'

                var = self._generate_clean_var(concept.split('.')[0], used_vars)

                nodes[t_id] = {
                    'var': var,
                    'concept': concept,
                    'edges': []
                }

                # QUESTION
                if (
                    is_question
                    and lemma in self.QUESTION_WORDS
                    and self.enabled("QUESTION")
                ):
                    self.rule_counts["QUESTION"] += 1
                    nodes[t_id]['edges'].append((':mode','amr-unknown'))

                # NEGATION
                for p_not in sent:

                    if (
                        p_not.get('lemma','').lower() in ['não','nunca']
                        and str(p_not['head']) == t_id
                        and self.enabled("NEGATION")
                    ):
                        self.rule_counts["NEGATION"] += 1
                        nodes[t_id]['edges'].append((':polarity','-'))

                # SUBJECT INSERTION
                if upos == 'VERB':

                    subj_lemma = self.sub_ins.get_virtual_node(tok)

                    has_subj = any(
                        t['head']==tok['id'] and t['deprel']=='nsubj'
                        for t in sent
                    )

                    if subj_lemma and not has_subj and self.enabled("SUBJECT_INSERTION"):

                        self.rule_counts["SUBJECT_INSERTION"] += 1

                        s_id = f"v_{t_id}"

                        nodes[s_id] = {
                            'var': self._generate_clean_var(subj_lemma, used_vars),
                            'concept': subj_lemma,
                            'edges': []
                        }

                        nodes[t_id]['edges'].append((':ARG0', s_id))

            # =========================
            # STRUCTURE (PROTECTED BY ABLATION)
            # =========================
            root_id = None

            for tok in sent:

                t_id = str(tok['id'])
                head_id = str(tok['head'])
                deprel_full = tok.get('deprel','dep')
                
                # Chave de ablação baseada na relação (ex: 'NSUBJ', 'NMOD_POSS')
                rule_key = deprel_full.upper().replace(":", "_")

                if head_id == '0':
                    root_id = t_id

                if t_id in nodes and head_id in nodes and t_id != head_id:

                    if deprel_full == 'nmod:poss':
                        self.rule_counts["POSSE"] += 1
                        if self.enabled("POSSE"):
                            nodes[head_id]['edges'].append((':poss', t_id))
                        continue

                    # Tenta mapear deprel_full primeiro, depois a deprel básica
                    target_deprel = None
                    if deprel_full in self.ud_to_amr:
                        target_deprel = deprel_full
                    elif deprel_full.split(':')[0] in self.ud_to_amr:
                        target_deprel = deprel_full.split(':')[0]

                    if target_deprel and self.enabled(rule_key):
                        # Incremento de contagem para regras de estrutura
                        if rule_key in self.rule_counts:
                            self.rule_counts[rule_key] += 1
                            
                        role = self.ud_to_amr[target_deprel]
                        nodes[head_id]['edges'].append((role, t_id))

            # =========================
            # CONTRAST
            # =========================
            contrast_token = None

            for tok in sent:
                if tok.get('lemma','').lower() in self.CONTRAST_WORDS:
                    contrast_token = tok
                    break

            if contrast_token and self.enabled("CONTRAST"):

                self.rule_counts["CONTRAST"] += 1

                contrast_id = f"contrast_{contrast_token['id']}"

                nodes[contrast_id] = {
                    'var': self._generate_clean_var('contrast', used_vars),
                    'concept': 'contrast-01',
                    'edges': []
                }

                root_id = contrast_id

            results.append({
                'nodes': nodes,
                'root': root_id
            })

        return results

    # =========================
    # SUPPORT
    # =========================
    def get_support(self):

        return {
            rule: (count / self.total_sentences if self.total_sentences else 0)
            for rule, count in self.rule_counts.items()
        }

    # =========================
    # VAR GENERATION
    # =========================
    def _generate_clean_var(self, lemma, used_vars):

        base = lemma[0].lower() if lemma and lemma[0].isalpha() else 'x'

        used_vars[base] = used_vars.get(base, 0) + 1

        return base if used_vars[base] == 1 else f"{base}{used_vars[base]}"