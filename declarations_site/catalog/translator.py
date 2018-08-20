import os.path
import re
from csv import reader
from collections import namedtuple, Counter

from translitua import translit
from pyquery import PyQuery as pq

from catalog.utils import is_cyr
from catalog.models import Translation


class Translator:
    def __init__(self):
        self.inner_dict = {}

    def get_id(self, term):
        return term.replace("\xa0", " ").replace("\u200b", "").lower().strip(" ,.;")

    def get_loose_id(self, term):
        return re.sub(
            "[.,\/#!$%\^&\*;:{}=\-_`~()\s]",
            "",
            term.replace("\xa0", " ").replace("\u200b", "").lower(),
        )

    def fetch_partial_dict_from_db(self, phrases):
        phrases = list(filter(None, phrases))
        ids = set(map(self.get_id, phrases)) | set(map(self.get_loose_id, phrases))
        translations = Translation.objects.filter(term_id__in=ids).values(
            "term_id", "translation", "source", "quality", "strict_id"
        )

        self.inner_dict = {v["term_id"]: v for v in translations}

    def load_dict_from_csv(self, fname, source, quality, ignore_header=True):
        with open(fname) as fp:
            r = reader(fp)
            if ignore_header:
                next(r)

            for l in r:
                if len(l) >= 2:
                    translation = dict(
                        term=l[0],
                        translation=l[1],
                        source=source,
                        quality=quality,
                        strict_id=True,
                    )

                    term_id = self.get_id(l[0])
                    loose_term_id = self.get_loose_id(l[0])

                    if not term_id:
                        continue

                    if term_id in self.inner_dict:
                        if quality < self.inner_dict[term_id]["quality"]:
                            continue

                    self.inner_dict[term_id] = translation

                    if not loose_term_id:
                        continue

                    if loose_term_id in self.inner_dict:
                        if quality < self.inner_dict[loose_term_id]["quality"]:
                            continue

                        if (
                            quality == self.inner_dict[loose_term_id]["quality"]
                            and self.inner_dict[loose_term_id]["strict_id"]
                        ):
                            continue

                    translation["strict_id"] = False
                    self.inner_dict[loose_term_id] = translation

    def translate(self, phrase):
        if not is_cyr(phrase):
            return dict(
                term=phrase, translation=phrase, source="not_required", quality=10
            )

        term_id = self.get_id(phrase)
        if term_id in self.inner_dict:
            return self.inner_dict[term_id]

        loose_term_id = self.get_loose_id(phrase)

        if loose_term_id in self.inner_dict:
            return self.inner_dict[loose_term_id]

        return dict(
            term=phrase, translation=translit(phrase), source="translit", quality=1
        )


class HTMLTranslator(Translator):
    def __init__(self, html, selectors):
        super().__init__()

        self._parsed_html = pq(html)
        self._html_elements = []

        for el in self._parsed_html(selectors):
            for x in el.getiterator():
                if x.text or x.tail:
                    self._html_elements.append(x)

        phrases = self.get_phrases()
        self.fetch_partial_dict_from_db(phrases)

    def get_phrases(self):
        phrases = []
        for el in self._html_elements:
            if el.text:
                phrases.append(el.text)
            if el.tail:
                phrases.append(el.tail)

        return phrases

    def get_translated_html(self):
        for el in self._html_elements:
            if el.text:
                phrase = self.translate(el.text)
                el.text = phrase["translation"]
            if el.tail:
                phrase = self.translate(el.tail)
                el.tail = phrase["translation"]

        return self._parsed_html.html()
