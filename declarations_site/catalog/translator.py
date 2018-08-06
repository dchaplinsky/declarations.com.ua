import os.path
import re
from csv import reader
from collections import namedtuple, Counter
from catalog.utils import is_cyr
from translitua import translit


class Phrase():
    __slots__ = ["term", "translation", "source", "quality", "usages"]

    def __init__(self, term, translation, source, quality, usages=0):
        self.term = term
        self.translation = translation
        self.source = source
        self.quality = quality
        self.usages = usages
    
    def inc_usages(self):
        self.usages += 1
    
    def __repr__(self):
        return "<{}> ({})".format(self.translation, self.source)

class Translator():
    def __init__(self, debug=False):
        self.inner_dict = {}
        self.loose_dict = {}
        self.unseen = Counter()
        self.debug = debug
    
    def get_id(self, term):
        return term.replace("\xa0", " ").replace("\u200b", "").lower().strip(" ,.;")

    def get_loose_id(self, term):
        return re.sub(
            "[.,\/#!$%\^&\*;:{}=\-_`~()\s]",
            "",
            term.replace("\xa0", " ").replace("\u200b", "").lower()
        )

    def load_dict_from_csv(self, fname, source, quality, ignore_header=True):
        with open(fname) as fp:
            r = reader(fp)
            if ignore_header:
                next(r)
            
            for l in r:
                if len(l) >= 2:
                    translation = Phrase(
                        term=l[0],
                        translation=l[1],
                        source=source,
                        quality=quality
                    )

                    term_id = self.get_id(l[0])
                    if term_id in self.inner_dict:
                        if quality < self.inner_dict[term_id].quality:
                            continue

                    if term_id:
                        self.inner_dict[term_id] = translation

                    loose_term_id = self.get_loose_id(l[0])
                    if loose_term_id in self.loose_dict:
                        if quality < self.loose_dict[loose_term_id].quality:
                            continue

                    if loose_term_id:
                        self.loose_dict[loose_term_id] = translation

    def translate(self, phrase):
        if not is_cyr(phrase):
            return Phrase(
                term=phrase,
                translation=phrase,
                source="not_required",
                quality=10
            ), "translation_not_required"

        term_id = self.get_id(phrase)
        if term_id in self.inner_dict:
            tr = self.inner_dict[term_id]
            tr.inc_usages()
            return tr, "exact"

        loose_term_id = self.get_loose_id(phrase)

        if loose_term_id in self.loose_dict:
            tr = self.loose_dict[loose_term_id]
            tr.inc_usages()
            return tr, "loose"

        if self.debug and phrase.strip():
            self.unseen.update([phrase.strip()])

        return Phrase(
            term=phrase,
            translation=translit(phrase),
            source="translit",
            quality=1
        ), "poor"
    
    def find_unused_strict(self):
        return [p for p in self.inner_dict.values() if p.usages==0]

    def find_unused_loose(self):
        return [p for p in self.loose_dict.values() if p.usages==0]


TRANSLATOR_SINGLETON = Translator()

CURR_DIR = os.path.dirname(__file__)
DICT_DIR = os.path.join(CURR_DIR, "data/dictionaries/")

TRANSLATOR_SINGLETON.load_dict_from_csv(os.path.join(DICT_DIR, "decl_translations.csv"), "translator", 10)
TRANSLATOR_SINGLETON.load_dict_from_csv(os.path.join(DICT_DIR, "pep_translations.csv"), "pep", 9)
TRANSLATOR_SINGLETON.load_dict_from_csv(os.path.join(DICT_DIR, "decl_translations.csv"), "google", 3)
