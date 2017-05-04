import xlsxwriter
from django.core.management.base import BaseCommand
from catalog.elastic_models import NACPDeclaration
from elasticsearch_dsl.query import Q, FunctionScore, ConstantScore


def resolve_hilite(res, field, default):
    if field in res.meta.highlight:
        return " ".join(res.meta.highlight[field])
    else:
        return default


def replace_hilight(s):
    return str(s).replace(
        "||!", '<span style="color: red">').replace("||", "</span>")


MARGIN_SCORE = 12


class Command(BaseCommand):
    help = 'Reunite corrected declarations with original ones'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.global_matches = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Show debug information on each match (A LOT OF TEXT)',
        )

        parser.add_argument(
            '--store_matches',
            dest='store_matches',
            default="",
            help='Store each match to HUGE XLSX file for further analysis',
        )

    def store_example(self, orig, matches, debug=False, store_matches=False):
        orig_family = ", ".join(sorted(
            fam.family_name for fam in getattr(orig.general, "family", [])
        ))

        if debug:
            self.stdout.write(
                "ORIG: %s %s %s %s %s" % (
                    orig.general.full_name, orig.general.post.post,
                    orig.general.post.office, orig.general.post.region,
                    orig_family
                )
            )

        result = False
        if len(matches) == 0:
            self.stderr.write("Cannot reconcile %s, http://declarations.com.ua/declaration/%s" % (
                orig.general.full_name, orig.meta.id))

        for pos, a in enumerate(matches):
            if debug:
                cand_family = ", ".join(sorted(
                    fam.family_name for fam in getattr(a.general, "family", [])
                ))

                self.stdout.write(
                    "Candidate #%s: %s %s %s %s %s (%s)" % (
                        pos + 1, a.general.full_name,
                        a.general.post.post, a.general.post.office,
                        a.general.post.region, cand_family, a._score
                    )
                )

            if store_matches:
                full_name = resolve_hilite(
                    a, "general.full_name", a.general.full_name)
                post = resolve_hilite(
                    a, "general.post.post", a.general.post.post)
                office = resolve_hilite(
                    a, "general.post.office", a.general.post.office)
                region = resolve_hilite(
                    a, "general.post.region", a.general.post.region)

                if "general.family.family_name" in a.meta.highlight:
                    family = " ".join(
                        a.meta.highlight["general.family.family_name"])
                else:
                    family = ", ".join(
                        sorted(
                            [f.family_name
                                for f in getattr(a.general, "family",  [])]
                        )
                    )

                self.global_matches.append({
                    "pos": pos,
                    "score": a._score,
                    "orig_year": orig.intro.declaration_year,
                    "orig_date": orig.intro.date,
                    "orig_doc_type": orig.intro.doc_type,
                    "orig_full_name": orig.general.full_name,
                    "orig_post": orig.general.post.post,
                    "orig_office": orig.general.post.office,
                    "orig_region": orig.general.post.region,
                    "orig_family": orig_family,

                    "cand_year": a.intro.declaration_year,
                    "cand_date": a.intro.date,
                    "cand_doc_type": a.intro.doc_type,
                    "cand_full_name": full_name,
                    "cand_post": post,
                    "cand_office": office,
                    "cand_region": region,
                    "cand_family": family
                })

            if a._score > MARGIN_SCORE and pos == 0:
                a.original_declarations = [a.meta.id]
                orig.corrected_declarations = [orig.meta.id]

                a.save()
                orig.save()

                result = True

        return result

    def handle(self, *args, **options):
        corrected = NACPDeclaration.search().filter(
            "term", intro__corrected=True)

        cntr = 0
        success_rate = 0
        for i, d in enumerate(corrected.scan()):
            must = [
                ConstantScore(
                    query=Q(
                        "multi_match",
                        query=d.general.full_name,
                        operator="and",
                        fields=[
                            "general.last_name",
                            "general.name",
                            "general.patronymic",
                            "general.full_name",
                        ],
                    ),
                    boost=10
                )
            ]

            should = [
                ConstantScore(
                    query=Q(
                        "match",
                        general__post__post={
                            "query": d.general.post.post,
                            "minimum_should_match": "50%"
                        },
                    ),
                    boost=2
                ),
                ConstantScore(
                    query=Q(
                        "match",
                        general__post__office={
                            "query": d.general.post.office,
                            "minimum_should_match": "50%"
                        },
                    ),
                    boost=2
                ),
                ConstantScore(
                    query=Q(
                        "match",
                        general__post__region={
                            "query": d.general.post.region.replace(
                                " область", ""),
                            "minimum_should_match": "60%"
                        },
                    ),
                    boost=1
                )
            ]

            for fam in getattr(d.general, "family", []):
                should.append(
                    ConstantScore(
                        query=Q(
                            "multi_match",
                            query=fam.family_name,
                            operator="and",
                            fields=[
                                "general.family.family_name"
                            ]
                        ),
                        boost=2
                    )
                )

            candidates = NACPDeclaration.search() \
                .query(
                    FunctionScore(
                        query=Q("bool", must=must, should=should),
                        score_mode="sum"
                    )
                ) \
                .filter("term",
                    intro__declaration_year=d.intro.declaration_year) \
                .query(~Q('term', _id=d.meta.id)) \
                .filter("term", intro__corrected=False) \
                .query(
                    ConstantScore(
                        query=Q("term", intro__doc_type=d.intro.doc_type),
                        boost=0
                    )
                )

            if options["store_matches"]:
                candidates = candidates \
                    .highlight_options(
                        order='score', fragment_size=500,
                        number_of_fragments=100, pre_tags=['||!'],
                        post_tags=["||"]) \
                    .highlight(
                        "general.full_name", "general.post.region",
                        "general.post.office", "general.post.post",
                        "general.family.family_name")

            candidates = candidates.execute()

            success = self.store_example(
                d, candidates, debug=options["debug"],
                store_matches=options["store_matches"])

            if success:
                success_rate += 1

            cntr += 1

            if cntr and cntr % 5000 == 0:
                self.stdout.write(
                    "%s declarations processed, SR: %s%%" % (cntr, success_rate / cntr * 100)
                )

        self.stdout.write(
            "%s declarations processed, SR: %s%%" % (cntr, success_rate / cntr * 100)
        )

        if options["store_matches"]:
            self.save_to_excel(options["store_matches"])

    def save_to_excel(self, fname):
        workbook = xlsxwriter.Workbook(fname)
        hits_worksheet = workbook.add_worksheet()
        mediocre_worksheet = workbook.add_worksheet() 
        misses_worksheet = workbook.add_worksheet()

        # Set up some formats to use.
        bold_red = workbook.add_format({'bold': True, 'color': 'red'})

        IS_HIT = 2
        IS_MEDIOCRE = 1
        IS_MISS = 0

        def is_hit(rec):
            if rec["score"] > MARGIN_SCORE:
                if rec["pos"] == 0:
                    return IS_HIT
                else:
                    return IS_MEDIOCRE
            else:
                return IS_MISS

        hits_row = 1
        mediocre_row = 1
        misses_row = 1

        fields = [
            "pos",
            "score",
            "orig_year",
            "cand_year",
            "orig_date",
            "cand_date",
            "orig_doc_type",
            "cand_doc_type",
            "orig_full_name",
            "cand_full_name",
            "orig_post",
            "cand_post",
            "orig_office",
            "cand_office",
            "orig_region",
            "cand_region",
            "orig_family",
            "cand_family",
        ]

        def parse_hilited_str(s):
            for chunk in str(s).split("||"):
                if chunk.startswith("!"):
                    yield bold_red
                    yield chunk.strip().lstrip("!")
                else:
                    yield chunk

        for i, f in enumerate(fields):
            hits_worksheet.write(0, i, f)
            misses_worksheet.write(0, i, f)
            mediocre_worksheet.write(0, i, f)

        for rec in self.global_matches:
            cls = is_hit(rec)
            if cls == IS_HIT:
                ws = hits_worksheet
                row = hits_row
            elif cls == IS_MEDIOCRE:
                ws = mediocre_worksheet
                row = mediocre_row
            else:
                ws = misses_worksheet
                row = misses_row

            for i, f in enumerate(fields):
                if f.startswith("cand_"):
                    content_to_write = list(
                        filter(None, parse_hilited_str(rec[f])))
                    if content_to_write:
                        ws.write_rich_string(row, i, *content_to_write)
                else:
                    ws.write(row, i, rec[f])

            if cls == IS_HIT:
                hits_row += 1
            elif cls == IS_MEDIOCRE:
                mediocre_row += 1
            else:
                misses_row += 1

        workbook.close()
