# RBAMR-News
RBAMR-News is a symbolic and rule-based AMR parsing project for Brazilian Portuguese news texts. The repository investigates the portability and effectiveness of handcrafted AMR rules originally developed for literary Portuguese, adapting them to the journalistic domain through modern NLP pipelines and dependency-based semantic processing. The project revisits the original RBAMR parser proposed by [Anchiêta and Pardo (2018)](https://github.com/rafaelanchieta/rbamr?tab=readme-ov-file), a rule-based AMR parsing architecture originally developed for the AMR-LittlePrince corpus.

The project is grounded on the research presented in:

> **Towards RBAMR-News: a Rule-Based AMR Parser for News in Portuguese**

---

# Abstract

RBAMR-News aims to develop a rule-based Abstract Meaning Representation (AMR) parser for Brazilian Portuguese news texts using contemporary NLP technologies while revisiting the original RBAMR symbolic architecture.

The project explores the possibilities of reenginering the original RBAMR parser pipeline using modern syntactic parsing and semantic processing tools in order to evaluate whether symbolic AMR rules designed for literary texts can generalize to journalistic language.

The parser is evaluated on **AMRNews-PT**, the only manually annotated AMR news corpus currently available for Portuguese.

---

# What is AMR?

Abstract Meaning Representation (AMR) is a semantic formalism that represents sentence meaning as rooted directed graphs.

AMR abstracts away from surface syntax and focuses on semantic structure, including:

- events;
- participants;
- semantic roles;
- negation;
- modality;
- coordination;
- temporal relations;
- coreference;
- discourse relations.

Example:

Sentence:

```text
Mary bought a car yesterday.
```

AMR representation:

```text
(b / buy-01
   :ARG0 (p / person :name "Mary")
   :ARG1 (c / car)
   :time (d / date-entity :day "yesterday"))
```

---

# Motivation

Recent AMR parsers rely heavily on:

- large annotated corpora;
- transformer architectures;
- expensive training procedures.

However, Brazilian Portuguese remains a low-resource language for AMR.

Currently available AMR corpora in Portuguese are limited in:

- size;
- genre diversity;
- domain coverage.

RBAMR-News addresses this problem through a symbolic and interpretable rule-based approach.

---

# Portuguese AMR Resources

| Corpus | Genre | Size |
|---|---|---|
| AMR-LittlePrince | Literature | 1,527 |
| DANTESTocks-AMR | Tweets | 1,128 |
| AMRNews-PT | News | 870 |
| OpiSums-PT-AMR | Reviews | 404 |
| AMRScien-Br-Corpus | Popular science | 200 |

---

# Project Goals

The project aims to:

1. Reconstruct the original RBAMR parser using modern NLP tools.
2. Adapt AMR rules from literary Portuguese to news texts.
3. Evaluate rule portability across domains.
4. Support semi-automatic AMR annotation for Portuguese.
5. Investigate symbolic AMR parsing for low-resource languages.
6. Build a larger news annotated corpus in the future.

---

# Architecture

RBAMR-News follows a pipeline-inspired symbolic architecture.

```text
Input Text
   ↓
Syntactic Parsing
   ↓
Semantic Role Labeling
   ↓
Rule-Based AMR Generation
   ↓
AMR Graph
```

---

# Pipeline Components

## 1. Syntactic Parsing

The project uses:

- **[PortParser v2](https://huggingface.co/spaces/NILC-ICMC-USP/Portparser.v2)**
- Universal Dependencies (UD)
- CoNLL-U representations

PortParser was selected due to its high parsing accuracy for Brazilian Portuguese.

---

## 2. Semantic Role Labeling (SRL)

The original RBAMR used Brazilis SRL.

RBAMR-News reconstructs SRL using:

- dependency-based heuristics;
- Verbo-Brasil;
- UD syntactic relations;
- semantic argument mappings.

The system identifies:

- predicates;
- subjects;
- objects;
- oblique arguments;
- implicit subjects.

Fallback semantic frames are generated when predicates are missing from Verbo-Brasil.

Example:

```text
lemma.01
```

---

## 3. Rule-Based AMR Generation

The core of the project is the symbolic AMR rule engine.

Rules transform dependency structures into AMR graphs.

The rules were adapted from the original RBAMR parser to Universal Dependencies.

---

# Rule Categories

## Lexical and Morphosyntactic Rules

These rules handle:

- auxiliary verbs;
- subject insertion;
- ordinals;
- stopword filtering.

Examples:

| Original | Adaptation |
|---|---|
| PALAVRAS AUX | UD AUX + Hartmann rules |
| morphology | virtual pronoun insertion |

---

## Named Entity Rules

Named entities are converted into AMR name structures.

Example:

```text
(name
   :op1 "Michael"
   :op2 "Jackson")
```

---

## Argument Structure Rules

These rules map syntactic dependencies into semantic roles.

| UD Relation | AMR Relation |
|---|---|
| nsubj | :ARG0 |
| obj | :ARG1 |
| iobj | :ARG2 |
| xcomp | :ARG2 |

---

## Syntactic-Semantic Rules

The parser handles several semantic phenomena:

| Phenomenon | AMR Relation |
|---|---|
| adjectival modification | :mod |
| negation | :polarity - |
| quantity | :quant |
| possession | :poss |
| coordination | :op |
| contrast | :contrast |
| time | :time |
| degree | :degree |
| manner | :manner |

---

# Supported Linguistic Phenomena

RBAMR-News includes support for:

- auxiliary constructions;
- passive voice;
- implicit subjects;
- coordination;
- negation;
- modality;
- copular constructions;
- quantification;
- named entities;
- contrastive discourse markers;
- interrogatives.

---

# Example Rules

## Subject Mapping

```text
nsubj → :ARG0
```

## Direct Object Mapping

```text
obj → :ARG1
```

## Negation

```text
não / nunca → :polarity -
```

## Modality

```text
poder → :possible
dever → :obligate
```

---

# Dataset

The parser is evaluated on:

## AMRNews-PT

Characteristics:

- 870 manually annotated sentences;
- journalistic texts;
- extracted from Folha de São Paulo;
- sentences up to 23 tokens;
- annotated using Verbo-Brasil.

The corpus was manually annotated by researchers in:

- Computational Linguistics;
- Computer Science.

Inter-annotator agreement:

```text
Smatch = 0.73
```

---

# Evaluation

RBAMR-News evaluates both:

- rule-level performance;
- graph-level semantic quality.

---

## Metrics

### Rule-Level Metrics

- support;
- precision;
- recall;
- F1-score.

### Graph-Level Metric

- Smatch.

---

# Ablation Study

The project performs systematic ablation experiments.

Each rule is individually removed to measure its contribution.

Formula:

```text
ΔS = Sfull − Sablated
ΔP = Pfull − Pablated
ΔR = Rfull − Rablated
```

---

# Results

## Overall Performance

| Metric | Value |
|---|---|
| Precision | 0.43 |
| Recall | 0.64 |
| Smatch F1 | 0.51 |

---

## Fine-Grained Performance

| Category | F1-score |
|---|---|
| Concepts | 0.56 |
| Relations | 0.39 |

---

# Most Important Rules

The ablation study shows that the most impactful rules are:

| Rule | Impact |
|---|---|
| Subject → :ARG0 | High |
| Direct Object → :ARG1 | High |
| Named Entities | High |

Lower-impact rules include:

- ordinals;
- possession;
- copular constructions.

---

# Technologies

The project uses:

| Technology | Purpose |
|---|---|
| Python | Main implementation |
| PortParser | Dependency parsing |
| Universal Dependencies | Syntax representation |
| Verbo-Brasil | Semantic frames |
| PENMAN | AMR serialization |
| Smatch | Evaluation |

---

# Methodological Perspective

RBAMR-News adopts a:

## Hybrid Neuro-Symbolic Approach

Combining:

- symbolic linguistic rules;
- dependency parsing;
- semantic role heuristics;
- lexical-semantic resources;
- interpretable semantic processing.

---

# Applications

Possible applications include:

- semantic parsing;
- information extraction;
- summarization;
- question answering;
- semantic search;
- machine translation;
- corpus annotation support;
- low-resource NLP research.

---

# Citation

If you use this repository, please cite: Hidden Information

---

# References

Main references include:

- Banarescu et al. (2013)
- Anchieta and Pardo (2018; 2022)
- Sobrevilla Cabezudo and Pardo (2019)
- Mansouri (2025)
- Wein and Opitz (2024)

---

# Author

Developed and maintained by Hidden Information.

---

# Repository

Hidden Information
