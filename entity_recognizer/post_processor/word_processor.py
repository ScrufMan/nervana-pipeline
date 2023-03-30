import requests


def lemmatize_text(text):
    url = "https://lindat.mff.cuni.cz/services/morphodita/api/analyze?output=json&convert_tagset=pdt_to_conll2009"
    params = {'data': text}
    response = requests.get(url, params=params)
    response.raise_for_status()
    lemmas = response.json()
    if lemmas:
        lematized_text = ""
        for lematized_part in lemmas["result"]:
            for word_part in lematized_part:
                lematized_text += word_part["analyses"][0]["lemma"].lower()
                lematized_text += word_part.get("space", "")
        return lematized_text
    else:
        return text
