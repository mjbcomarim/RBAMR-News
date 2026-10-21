# RBAMR-News

**A symbolic and neuro-symbolic AMR parser for Brazilian Portuguese news texts**

RBAMR-News is a research project for **Abstract Meaning Representation (AMR) parsing in Brazilian Portuguese**, with a particular focus on the **journalistic domain** and low-resource semantic parsing.

The project revisits and extends the original **RBAMR** parser proposed by Anchiêta and Pardo (2018). RBAMR-News reconstructs its symbolic architecture using modern NLP tools, Universal Dependencies, Semantic Role Labeling, and an expanded set of linguistic rules designed for Brazilian Portuguese.

The current research investigates a central question:

> **How far can linguistically motivated symbolic rules go in AMR parsing for Brazilian Portuguese, and how much can they benefit from neural semantic information?**

RBAMR-News is under active development as part of doctoral research in Computational Linguistics at the **Federal University of São Carlos (UFSCar)** and the **Interinstitutional Center for Computational Linguistics (NILC)**.

---

## Overview

RBAMR-News converts Brazilian Portuguese sentences into AMR graphs through a modular pipeline:

```text
Brazilian Portuguese text
          │
          ▼
   Syntactic Parsing
  Universal Dependencies
          │
          ▼
 Semantic Information
  ├── symbolic heuristics
  └── neural SRL
          │
          ▼
 Linguistic Processing
  ├── implicit subjects
  ├── auxiliary verbs
  ├── named entities
  └── lexical normalization
          │
          ▼
   UD/SRL → AMR Rules
          │
          ▼
      AMR Graph
          │
          ▼
 Evaluation / Human Revision
```

The system is designed not only as an AMR parser, but also as an experimental environment for investigating **interpretable semantic parsing**, **rule portability**, and **semi-automatic AMR corpus construction**.

---

## Research Goals

RBAMR-News currently pursues five main goals:

1. **Modernize RBAMR** by reconstructing the original parser in Python 3 and replacing obsolete NLP components.

2. **Adapt symbolic AMR rules to Universal Dependencies**, making the architecture compatible with contemporary Brazilian Portuguese syntactic parsing.

3. **Adapt the parser to journalistic Portuguese**, investigating the portability of rules originally developed for literary texts.

4. **Integrate Semantic Role Labeling**, comparing symbolic and neural semantic information in AMR generation.

5. **Support semi-automatic AMR annotation**, reducing the amount of manual work required to construct larger Brazilian Portuguese AMR corpora.

---

## Background

### What is AMR?

**Abstract Meaning Representation (AMR)** represents sentence meaning as a rooted, directed graph.

For example:

```text
Maria comprou um carro.
```

A simplified AMR representation is:

```penman
(c / comprar-01
   :ARG0 (p / person
             :name (n / name
                      :op1 "Maria"))
   :ARG1 (c2 / carro))
```

AMR represents semantic concepts and relations rather than the surface syntactic structure of the sentence.

Typical phenomena represented in AMR include:

- predicate–argument structure;
- semantic roles;
- named entities;
- negation;
- modality;
- quantities;
- temporal information;
- coordination;
- coreference;
- discourse relations.

---

## Why RBAMR-News?

Most modern AMR parsers depend on large annotated datasets and neural architectures.

For Brazilian Portuguese, however, AMR remains a **low-resource task**. Available corpora are relatively small and cover only a limited number of textual domains.

RBAMR-News therefore investigates an alternative and complementary strategy:

> combining explicit linguistic knowledge with modern syntactic and semantic NLP components.

This makes it possible to inspect exactly **why** a semantic relation was generated and to evaluate individual linguistic rules through controlled experiments.

---

## From RBAMR to RBAMR-News

The original RBAMR parser was developed for the Portuguese translation of *The Little Prince*.

RBAMR-News revisits this architecture in a substantially different computational environment.

| RBAMR | RBAMR-News |
|---|---|
| Literary domain | Journalistic domain |
| Legacy NLP pipeline | Modern Brazilian Portuguese NLP |
| Original dependency representation | Universal Dependencies |
| Brazilis SRL | Symbolic and neural SRL experiments |
| Original handcrafted rules | Revised and expanded AMR rules |
| Legacy implementation | Python 3 implementation |
| Literary AMR corpus | AMRNews-PT evaluation |

The goal is therefore not merely to reproduce RBAMR, but to investigate how its symbolic assumptions behave when transferred to a different **domain, syntactic representation, and semantic pipeline**.

---

## Pipeline

### 1. Syntactic Parsing

Input sentences are represented using **Universal Dependencies (UD)** in CoNLL-U format.

The pipeline uses Brazilian Portuguese dependency parsing as its syntactic foundation.

Relevant UD information includes:

```text
UPOS
HEAD
DEPREL
FEATS
LEMMA
```

These annotations provide the structural information used by subsequent AMR rules.

---

### 2. Semantic Role Labeling

RBAMR-News supports experiments with different sources of semantic information.

#### Symbolic SRL

Semantic roles can be inferred from:

- dependency relations;
- predicate information;
- Verbo-Brasil frames;
- handcrafted argument mappings.

#### Neural SRL

The current experimental pipeline also supports neural Semantic Role Labeling for Brazilian Portuguese.

Neural predictions are incorporated into the intermediate CoNLL-U representation and subsequently used during AMR generation.

This makes it possible to compare:

```text
Syntactic information only
        ↓
Symbolic semantic processing
        ↓
Neural semantic processing
        ↓
AMR quality
```

---

## Linguistic Processing

Before and during AMR generation, the system performs several normalization and linguistic processing steps.

These include:

- implicit subject insertion;
- subject inheritance;
- auxiliary verb normalization;
- named entity processing;
- lexical normalization;
- number normalization;
- predicate identification;
- semantic role mapping.

These modules are particularly important for Brazilian Portuguese phenomena such as **pro-drop subjects** and complex verbal constructions.

---

## UD → AMR Mapping

A central component of RBAMR-News is the mapping between syntactic dependencies and semantic relations.

Examples include:

| UD relation | Default AMR mapping |
|---|---|
| `nsubj` | `:ARG0` |
| `nsubj:pass` | `:ARG1` |
| `obj` | `:ARG1` |
| `iobj` | `:ARG2` |
| `xcomp` | `:ARG2` |
| `amod` | `:mod` |
| `nummod` | `:quant` |
| temporal modifiers | `:time` |
| emphatic adverbs | `:degree` |

These mappings are not intended as universal equivalences between syntax and semantics. They function as **default hypotheses** that can be modified by lexical, semantic, and construction-specific rules.

---

## Supported Phenomena

The current parser includes rules for phenomena such as:

### Predicate–argument structure

```text
nsubj → :ARG0
obj   → :ARG1
iobj  → :ARG2
```

### Negation

```text
não / nunca → :polarity -
```

### Named entities

```penman
(p / person
   :name (n / name
            :op1 "Maria"))
```

### Quantification

```text
nummod → :quant
```

### Modification

```text
amod → :mod
```

### Temporal information

```text
temporal modifier → :time
```

### Possession

```text
possessive construction → :poss
```

### Coordination

Coordination structures are represented using AMR operand relations such as:

```text
:op1
:op2
...
```

### Contrast

Contrastive markers such as:

```text
mas
porém
contudo
todavia
entretanto
```

can trigger explicit contrast structures.

### Copular constructions

Special rules investigate the AMR representation of copular predicates, including the use of:

```text
:domain
```

### Interrogatives

The system includes rules for interrogative structures and AMR representations involving unknown arguments or confirmation requests.

### Implicit subjects

Because Brazilian Portuguese is a pro-drop language, RBAMR-News includes procedures for recovering implicit subjects and propagating subjects across selected syntactic structures.

---

## Auxiliary Verbs

The parser includes specific treatment of Brazilian Portuguese auxiliary and semi-auxiliary constructions.

Examples include:

```text
acabar de
começar a
continuar a
deixar de
dever
estar para
haver de
ir
poder
ter de
ter que
tornar a
vir a
voltar a
```

These constructions are normalized before or during AMR generation so that auxiliary material does not automatically become an independent semantic predicate.

---

## Named Entities

RBAMR-News converts named entities into AMR-compatible `:name` structures.

The system can combine:

- local geographic resources;
- capitalization heuristics;
- entity-type heuristics;
- optional external entity information.

Example:

```penman
(c / city
   :name (n / name
            :op1 "São"
            :op2 "Paulo"))
```

---

## Data

### AMRNews-PT

The main evaluation resource is **AMRNews-PT**, a manually annotated AMR corpus for Brazilian Portuguese journalistic texts.

The corpus contains approximately **870 sentences** derived from *Folha de S.Paulo* news texts.

It provides an important testbed for evaluating whether symbolic rules developed in another domain can be transferred to journalistic Portuguese.

> **Important:** AMRNews-PT is an external research resource and is not redistributed here unless its original licensing conditions explicitly permit redistribution.

---

## Current Experimental Variants

The project has evolved through several experimental configurations.

| Configuration | Description |
|---|---|
| Symbolic | Dependency-based symbolic pipeline |
| Neural SRL v1 | Initial integration of neural semantic roles |
| Neural SRL v2 | Revised integration and structural corrections |
| Neural SRL + entity information | Neural semantic pipeline with expanded entity processing |

This progression allows the contribution of individual components to be evaluated independently.

---

## Current Results

Evaluation is performed with **Smatch**, using aligned gold and automatically generated AMR graphs.

On the current paired evaluation set, development has produced the following progression:

| System | Smatch F1 |
|---|---:|
| Symbolic baseline | 52.00 |
| Neural SRL – first integration | 54.12 |
| Neural SRL – revised integration | 57.43 |
| Neural SRL + expanded entity processing | **58.07** |

For the current best configuration:

```text
Precision: 65.12
Recall:    52.40
F1:        58.07
```

Concept identification reaches approximately:

```text
Concept F1: 61.65
```

These numbers correspond to the current experimental setup and should be interpreted as **research results rather than a stable benchmark release**.

---

## Evaluation

RBAMR-News is evaluated at multiple levels.

### Graph-level evaluation

The primary metric is:

```text
Smatch
```

Smatch measures overlap between predicted and gold AMR triples.

### Fine-grained analysis

The project also investigates:

- concepts;
- semantic relations;
- `:ARG0`;
- `:ARG1`;
- `:ARG2`;
- named entities;
- `:domain`;
- structural validity;
- graph connectivity.

### Error Analysis

Quantitative evaluation is complemented by qualitative analysis of:

- best-performing sentences;
- worst-performing non-zero sentences;
- zero-Smatch cases;
- recurrent linguistic phenomena;
- SRL-to-AMR propagation errors;
- lexical mismatches;
- structural graph errors.

---

## Ablation Experiments

Because RBAMR-News is modular and rule-based, individual components can be disabled to estimate their contribution.

For a component \(r\):

```text
ΔSmatch = Smatch(full system) − Smatch(system without r)
```

This methodology makes it possible to distinguish rules that are linguistically plausible from rules that actually improve AMR generation empirically.

---

## Running RBAMR-News

> **Development status:** the software is currently a research prototype. Interfaces and command-line options may change as the parser is developed.

A typical parser execution follows the general pattern:

```bash
python run_parser.py \
    --input INPUT.conllu \
    --output OUTPUT.txt \
    --srl-mode neural \
    --strict-graphs
```

For experiments without external entity processing:

```bash
python run_parser.py \
    --input INPUT.conllu \
    --output OUTPUT.txt \
    --srl-mode neural \
    --no-wiki \
    --strict-graphs
```

Selected linguistic rules can also be disabled for ablation experiments. For example:

```bash
python run_parser.py \
    --input INPUT.conllu \
    --output OUTPUT.txt \
    --srl-mode neural \
    --no-wiki \
    --strict-graphs \
    --disable-copula-domain
```

---

## Input

The parser currently operates primarily on **CoNLL-U-style representations** containing the syntactic and, depending on the experiment, semantic information required by the pipeline.

Example:

```text
# sent_id = example
# text = Maria comprou um carro.
...
```

The exact column requirements depend on the selected SRL mode.

---

## Output

The primary output is AMR serialized in PENMAN notation.

Example:

```penman
(c / comprar-01
   :ARG0 (p / person
             :name (n / name
                      :op1 "Maria"))
   :ARG1 (c2 / carro))
```

---

## Installation

The project is implemented in **Python 3**.

A complete reproducible environment specification is being prepared as the research codebase is consolidated.

Recommended workflow:

```bash
git clone https://github.com/mjbcomarim/RBAMR-News.git
cd RBAMR-News
```

Then create an isolated Python environment before installing the project dependencies.

> A pinned dependency file and fully reproducible installation procedure should be considered part of the next stable repository release.

---

## Repository Organization

The repository is being reorganized toward the following structure:

```text
RBAMR-News/
│
├── src/                  # Parser implementation
├── data/                 # Data and input examples
├── resources/            # Lexical and linguistic resources
├── evaluation/           # Smatch and evaluation scripts
├── experiments/          # Experimental configurations
├── docs/                 # Extended documentation
├── tests/                # Automated tests
│
├── run_parser.py         # Main parser entry point
├── requirements.txt      # Python dependencies
├── README.md
├── CITATION.cff
└── LICENSE
```

The exact structure may change while the research prototype is consolidated.

---

## Research Roadmap

### Parser

- [x] Reconstruct core symbolic RBAMR architecture
- [x] Migrate processing to Universal Dependencies
- [x] Implement basic UD → AMR mappings
- [x] Implement implicit-subject processing
- [x] Expand auxiliary-verb handling
- [x] Implement named-entity processing
- [x] Integrate neural SRL
- [x] Add rule ablation switches
- [ ] Consolidate the parser as a stable Python package
- [ ] Expand automated testing
- [ ] Improve graph structural validation

### Evaluation

- [x] Evaluate against AMRNews-PT
- [x] Perform Smatch evaluation
- [x] Compare symbolic and neural-SRL variants
- [x] Begin systematic qualitative error analysis
- [ ] Complete rule-level ablation analysis
- [ ] Expand linguistic phenomenon evaluation
- [ ] Publish reproducible experiment configurations

### Annotation Support

- [ ] Sentence-level interactive parsing
- [ ] File-level parsing
- [ ] Manual AMR graph editing
- [ ] Export human-corrected AMR
- [ ] Explicitly distinguish automatic output from human revision

---

## Limitations

RBAMR-News is currently an **experimental research parser**, not a production NLP system.

Current limitations include:

- dependence on upstream syntactic and semantic predictions;
- incomplete lexical coverage;
- incomplete coverage of Brazilian Portuguese constructions;
- errors propagated from SRL to AMR;
- difficulties with complex sentence structures;
- named-entity typing errors;
- graph connectivity errors in some constructions;
- limited AMR training and evaluation resources for Brazilian Portuguese.

A major objective of the project is precisely to identify and quantify these limitations.

---

## Reproducibility

Reproducibility is an ongoing priority of the project.

Stable experimental releases should document:

- parser version;
- input data version;
- SRL configuration;
- enabled and disabled rules;
- external resources;
- evaluation subset;
- Smatch configuration;
- random seeds when applicable.

Current Smatch experiments use multiple restarts and controlled evaluation settings.

---

## Technologies and Resources

RBAMR-News uses or interacts with:

- **Python 3**
- **Abstract Meaning Representation (AMR)**
- **Universal Dependencies**
- **CoNLL-U**
- **Semantic Role Labeling**
- **Verbo-Brasil**
- **PENMAN**
- **Smatch**
- Brazilian Portuguese dependency parsing resources

---

## Related Resources

The project builds upon or interacts with research on:

- RBAMR;
- AMR-LittlePrince;
- AMRNews-PT;
- Verbo-Brasil;
- Universal Dependencies;
- Brazilian Portuguese semantic role labeling;
- multilingual and low-resource AMR parsing.

---

## Research Context

RBAMR-News is part of doctoral research on **automatic methods for AMR corpus annotation in Brazilian Portuguese**.

The broader research agenda includes:

```text
Brazilian Portuguese corpora
          │
          ├── symbolic AMR parsing
          │
          ├── neural semantic role labeling
          │
          ├── linguistic rule analysis
          │
          ├── automatic AMR generation
          │
          └── human revision
                     │
                     ▼
          larger gold AMR resources
```

The long-term goal is not only to improve automatic parsing, but also to investigate how automatic systems can support the creation of **high-quality manually revised AMR corpora** for Brazilian Portuguese.

---

## Citation

If you use RBAMR-News in academic work, please cite the corresponding publication and/or software release.

A machine-readable `CITATION.cff` file will be provided with stable releases.

Related work:

**Towards RBAMR-News: a Rule-Based AMR Parser for News in Portuguese**

Full bibliographic information will be added after publication.

---

## Original RBAMR

RBAMR-News builds upon the original RBAMR architecture developed by **Rafael Anchiêta and Thiago Pardo**.

Original repository:

`rafaelanchieta/rbamr`

RBAMR-News should be understood as a reconstruction, modernization, and research extension of that work rather than as the original RBAMR implementation.

---

## Author

**Maria Julia Bernardo Comarim**

Graduate Program in Linguistics — PPGL/UFSCar  
Interinstitutional Center for Computational Linguistics — NILC  
Federal University of São Carlos — UFSCar

Research area: **Computational Semantics · Abstract Meaning Representation · Semantic Parsing · Brazilian Portuguese NLP**

---

## Acknowledgments

This research is developed at the **Federal University of São Carlos (UFSCar)** in connection with the **Interinstitutional Center for Computational Linguistics (NILC)**.

The project builds upon previous research on RBAMR, Brazilian Portuguese AMR resources, Universal Dependencies, Semantic Role Labeling, and Verbo-Brasil.

Research support and funding acknowledgments should follow the requirements applicable to the corresponding research outputs and software releases.

---

## Status

🚧 **Active research project**

RBAMR-News is under active development. Results, interfaces, rules, and experimental configurations may change as the parser and its evaluation are refined.

Issues, reproducibility reports, linguistic observations, and research-oriented contributions are welcome.
