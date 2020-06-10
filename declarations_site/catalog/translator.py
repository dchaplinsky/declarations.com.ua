import os.path
import re
from csv import reader
from collections import Counter
from html import unescape

from translitua import translit
from pyquery import PyQuery as pq

from catalog.utils import is_cyr


class NoOpTranslator:
    def translate(self, phrase, just_transliterate=False):
        return dict(term=phrase, translation=phrase, source="not_required", quality=10)


class Translator:
    def __init__(self, store_unseen=False):
        self.inner_dict = {}
        self.unseen = Counter()
        self.store_unseen = store_unseen

    @staticmethod
    def get_id(term):
        return (
            unescape(term)
            .replace("\xa0", " ")
            .replace("\u200b", "")
            .lower()
            .strip(" ,.;\t\n")
        )

    @staticmethod
    def get_loose_id(term):
        return re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()\s]", "", Translator.get_id(term))

    def load_dict(self, dct):
        for term in dct:
            term_id = term["term_id"]
            if term_id in self.inner_dict:
                if term["quality"] < self.inner_dict[term_id]["quality"]:
                    continue

            self.inner_dict[term_id] = term

    def _fetch_dict_from_db(self, phrases=None):
        from catalog.models import Translation

        if phrases is not None:
            phrases = list(filter(None, phrases))
            if not phrases:
                return

            ids = set(map(self.get_id, phrases)) | set(map(self.get_loose_id, phrases))
            q = Translation.objects.filter(term_id__in=ids)
        else:
            q = Translation.objects.all()

        translations = q.values(
            "term_id", "translation", "source", "quality", "strict_id"
        ).iterator()

        self.inner_dict = {v["term_id"]: v for v in translations if v["translation"]}

    def fetch_partial_dict_from_db(self, phrases):
        self._fetch_dict_from_db(phrases)

    def fetch_full_dict_from_db(self):
        self._fetch_dict_from_db()

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

    def auto_translate(self, phrase):
        res = []

        for s in map(str.strip, phrase.replace(".", ",").split(",")):
            gotcha = False

            if not is_cyr(s):
                res.append(s)
                continue

            for rex in [
                r"^[\d.,]+\s*\(га\)$",
                r"^[\d.,]+\s*\(соток\)$",
                r"^[\d.,]+\s*\(м²\)$",
                r"^[\d.,]+\s*куб\.?\s*см\.?$",
                r"^[\d.,]+\s*р\.?\s*н\.?$",
                r"^\d+\/\d+\s+част(ина|ини|ка|ки)\s*(квартири)?$",
                r"^[\d.,]+\s*л$",
                r"^[\d.,]+\s*ч$",
                r"^[\d.,]+\s*квт$",
                r"^[\d.,]+\s*см3$",
                r"^[\d.,]+\s*м$",
                r"^[\d.,]+\s*мм$",
                r"^[\d.,]+\s*см$",
                r"^[\d.,]+\s*р$",
                r"^[\d.,]+\s*л|к\.?\s*с\.?$",
                r"^[\d.,]+\s*куб\.?\s*дм\.?$",
            ]:
                if re.search(rex, s, flags=re.I):
                    gotcha = True
                    res.append(s)
                    break

            if not gotcha:
                return

        return dict(
            term=phrase, translation=", ".join(res), source="not_required", quality=10
        )

    def translate(self, phrase, just_transliterate=False):
        if not is_cyr(phrase):
            return dict(
                term=phrase, translation=phrase, source="not_required", quality=10
            )

        if just_transliterate:
            return dict(
                term=phrase, translation=translit(phrase), source="translit", quality=10
            )

        term_id = self.get_id(phrase)
        if term_id in self.inner_dict:
            return self.inner_dict[term_id]

        loose_term_id = self.get_loose_id(phrase)

        if loose_term_id in self.inner_dict:
            return self.inner_dict[loose_term_id]

        any_luck = self.auto_translate(phrase)
        if any_luck:
            return any_luck

        if phrase.strip() and self.store_unseen:
            self.unseen.update([phrase.strip()])

        return dict(
            term=phrase, translation=translit(phrase), source="translit", quality=1
        )


class HTMLTranslator(Translator):
    def __init__(
        self,
        html,
        selectors,
        extra_phrases=None,
        do_not_fetch_dicts=False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self._html_elements = []
        self._parsed_html = None
        if extra_phrases is None:
            extra_phrases = []

        phrases = extra_phrases

        if html:
            self._parsed_html = pq(str(html))
            self._html_elements = HTMLTranslator.get_html_elements(
                self._parsed_html, selectors
            )

            phrases += HTMLTranslator.get_phrases(self._html_elements)

        if not do_not_fetch_dicts:
            self.fetch_partial_dict_from_db(phrases)

    @staticmethod
    def get_html_elements(parsed_html, selectors):
        html_elements = []
        for el in parsed_html(selectors):
            for x in el.getiterator():
                if x.text or x.tail:
                    html_elements.append(x)

        return html_elements

    @staticmethod
    def get_phrases(html_elements):
        phrases = []
        for el in html_elements:
            if el.text:
                phrases.append(el.text)
            if el.tail:
                phrases.append(el.tail)

        return phrases

    def get_translated_html(self, do_not_translate=None):
        if do_not_translate is None:
            do_not_translate = []

        do_not_translate = [self.get_id(x) for x in do_not_translate]

        for el in self._html_elements:
            if el.text:
                if self.get_id(el.text) in do_not_translate:
                    continue

                phrase = self.translate(el.text)
                el.text = phrase["translation"]
            if el.tail:
                if self.get_id(el.tail) in do_not_translate:
                    continue

                phrase = self.translate(el.tail)
                el.tail = phrase["translation"]

        if self._parsed_html is None:
            return ""
        else:
            return self._parsed_html.html()
