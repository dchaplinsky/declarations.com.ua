from django.core.management.base import BaseCommand
from catalog.elastic_models import NACPDeclaration
from elasticsearch_dsl.query import Q, FunctionScore, ConstantScore


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

    def store_example(self, orig, matches, debug=False):
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

            if a._score > 12 and pos == 0:
                a.original_declarations = [orig.meta.id]
                orig.corrected_declarations = [a.meta.id]

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

            candidates = candidates.execute()

            success = self.store_example(d, candidates, debug=options["debug"])

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
