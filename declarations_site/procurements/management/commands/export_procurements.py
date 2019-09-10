import sys
import os.path
import json
import argparse
from datetime import date
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from procurements.models import Transactions
from django.core.serializers.json import DjangoJSONEncoder


class Command(BaseCommand):
    help = "Export transactions and nested data in jsonlines form"

    def add_arguments(self, parser):
        parser.add_argument(
            "out_file",
            type=argparse.FileType("w"),
            help="File to export serialized transactions",
            default=sys.stdout,
        )

        parser.add_argument(
            "--only_last_n_days", 
            type=int
        )

    def handle(self, *args, **options):
        qs = Transactions.objects.select_related(
            "seller",
            "purchase",
            "purchase__buyer",
            "purchase__buyer__region",
            "purchase__subject_type",
            "purchase__auction_type",
            "currency",
            "purchase_result_type",
        )

        if options["only_last_n_days"] is not None:
            qs = qs.filter(date__gte=date.today() - relativedelta(days=options["only_last_n_days"]))

        for transaction in tqdm(qs.iterator(), total=qs.count()):
            seller = model_to_dict(transaction.seller)
            purchase = model_to_dict(transaction.purchase)
            purchase["buyer"] = model_to_dict(transaction.purchase.buyer)
            purchase["buyer"]["region"] = model_to_dict(
                transaction.purchase.buyer.region
            )

            if transaction.purchase.subject_type is not None:
                purchase["subject_type"] = model_to_dict(
                    transaction.purchase.subject_type
                )

            purchase["auction_type"] = model_to_dict(transaction.purchase.auction_type)

            currency = model_to_dict(transaction.currency)

            transaction_dct = model_to_dict(transaction)
            transaction_dct["seller"] = seller
            transaction_dct["purchase"] = purchase
            transaction_dct["currency"] = currency

            if transaction.purchase_result_type is not None:
                transaction_dct["purchase_result_type"] = model_to_dict(
                    transaction.purchase_result_type
                )

            options["out_file"].write(
                "{}\n".format(json.dumps(transaction_dct, cls=DjangoJSONEncoder, ensure_ascii=False, sort_keys=True))
            )
