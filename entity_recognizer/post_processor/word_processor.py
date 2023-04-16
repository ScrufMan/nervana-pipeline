import requests


def lemmatize_text(text):
    url = "https://lindat.mff.cuni.cz/services/morphodita/api/analyze?output=json&convert_tagset=pdt_to_conll2009"
    payload = {'data': text}
    response = requests.post(url, data=payload)
    response.raise_for_status()
    lemmas = response.json()
    if lemmas:
        lemmatized_text = ""
        for lemmatized_part in lemmas["result"]:
            for word_part in lemmatized_part:
                lemmatized_text += word_part["analyses"][0]["lemma"].lower()
                lemmatized_text += word_part.get("space", "")
        return lemmatized_text
    else:
        return text
