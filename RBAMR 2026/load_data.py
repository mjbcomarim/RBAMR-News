def load_conllu(path):
    sentences = []
    sent = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                if sent:
                    sentences.append(sent)
                    sent = []
                continue

            if line.startswith("#"):
                continue

            parts = line.split("\t")

            if len(parts) != 10:
                continue

            token = {
                "id": int(parts[0]),
                "form": parts[1],
                "lemma": parts[2],
                "upos": parts[3],
                "head": int(parts[6]),
                "deprel": parts[7]
            }

            sent.append(token)

    if sent:
        sentences.append(sent)

    return sentences