from ufal.morphodita import *


class Lemmatizer:
    @staticmethod
    def lemmatize_text(text, tagger):
        tagset_converter = TagsetConverter.newPdtToConll2009Converter()
        forms = Forms()
        lemmas = TaggedLemmas()
        tokens = TokenRanges()
        tokenizer = tagger.newTokenizer()
        result_lemmas = []

        # Tag
        tokenizer.setText(text)
        while tokenizer.nextSentence(forms, tokens):
            tagger.tag(forms, lemmas)

            for lemma in lemmas:
                tagset_converter.convert(lemma)
                result_lemmas.append(lemma.lemma)

        return " ".join(result_lemmas)
