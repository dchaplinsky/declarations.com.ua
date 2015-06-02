"""
Knitr analytics generation command.
Requires recent R runtime and a number of R libraries, namely:
'knitr', 'knitrBootstrap', 'ggplot2', 'dplyr', 'xtable', 'scales', 'doBy'
They (and dependencies) in turn might require various devel packages to be installed on your system in order to compile.
See "install.packages" R command output for details.
"""
import os
import tempfile

from collections import defaultdict

from rpy2 import robjects
from rpy2.robjects.packages import importr
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.urlresolvers import reverse
from wagtail.wagtailcore.models import Site, Page

from catalog.elastic_models import Declaration
from cms_pages.models import RawHTMLPage


KNITR_SCRIPT_PATH = os.path.join(settings.BASE_DIR, 'catalog/data/declarations.Rmd')
STR_COLUMNS = ('name', 'region', 'city', 'work_region', 'post', 'office', 'foreign_country', 'f_foreign_country',
    'auto', 'auto_year', 'f_auto', 'f_auto_year', 'truck', 'truck_year', 'f_truck', 'f_truck_year', 'boat', 'boat_year',
    'f_boat', 'f_boat_year', 'plane', 'plane_year', 'f_plane', 'f_plane_year', 'other_vehicle', 'other_vehicle_year',
    'f_other_vehicle', 'f_other_vehicle_year')


class Command(BaseCommand):
    args = '<file_path>'
    help = ('Generates knitr analytics based on all available declarations.',)

    def handle(self, *args, **options):
        dump_to_file = len(args) > 0
        all_decls = Declaration.search().query('match_all').scan()
        table = self._generate_table(all_decls)
        report = self._run_knitr(table, fragment_only=not dump_to_file)

        if dump_to_file:
            file_path = args[0]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
        else:
            root_page = Site.objects.get(is_default_site=True).root_page
            try:
                analytics_page = root_page.get_children().get(slug=settings.ANALYTICS_SLUG).specific
            except Page.DoesNotExist:
                page_instance = RawHTMLPage(owner=None, title=settings.ANALYTICS_TITLE, slug=settings.ANALYTICS_SLUG)
                analytics_page = root_page.add_child(instance=page_instance)
            analytics_page.body = '<div class="analytics-wrapper">' + report + '</div>'
            revision = analytics_page.save_revision(user=None)
            revision.publish()
            self.stdout.write('Analytics page "{}" has been published.'.format(analytics_page.url))

    def _generate_table(self, declarations):
        """Generates an R data frame table from the list of declarations."""
        decl_table = defaultdict(list)
        for decl in declarations:
            decl_dict = self._map_fields(decl)
            # R DataFrame is column-major.
            for k, v in decl_dict.items():
                decl_table[k].append(v)
        return robjects.DataFrame(
            # Have to translate into a properly typed vector, otherwise R will treat the data in a bad way.
            {k: (robjects.StrVector(v) if k in STR_COLUMNS else robjects.FloatVector(v)) for k, v in decl_table.items()}
        )

    def _map_fields(self, declaration):
        """Maps declaration fields to a dictionary of format that reporting script expects."""
        def estate_space(estate):
            return [float(e['space'].replace(",", "."))
                    for e in estate if e['space']]

        def floatify(val):
            return float(val.replace(",", ".") or 0)

        return {
            'name': '<a href="{0}" target="_blank">{1} ({2})</a>'.format(
                reverse("details", kwargs={"declaration_id": declaration._id}),
                declaration.general.full_name,
                # temporary solution, should be removed once we'll have
                # analytics breakdown by year
                declaration.intro.declaration_year),
            'region': declaration.general.addresses[0].place,
            'city': declaration.general.addresses[0].place_city,
            'family_num': len(declaration.general.family_raw.split(';')) if declaration.general.family_raw else 0,
            'work_region': declaration.general.post.region,
            'post': declaration.general.post.post,
            'office': declaration.general.post.office,
            'year': int(declaration.intro.declaration_year),
            'income': floatify(declaration.income['5']['value']),
            'f_income': floatify(declaration.income['5']['family']),
            'salary': floatify(declaration.income['6']['value']),
            'f_salary': floatify(declaration.income['6']['family']),
            'job': floatify(declaration.income['7']['value']),
            'f_job': floatify(declaration.income['7']['family']),
            'author': floatify(declaration.income['8']['value']),
            'f_author': floatify(declaration.income['8']['family']),
            'dividends': floatify(declaration.income['9']['value'].rstrip('%')),
            'f_dividends': floatify(declaration.income['9']['family'].rstrip('%')),
            'help': floatify(declaration.income['10']['value']),
            'f_help': floatify(declaration.income['10']['family']),
            'gifts': floatify(declaration.income['11']['value']),
            'f_gifts': floatify(declaration.income['11']['family']),
            'jobless': floatify(declaration.income['12']['value']),
            'f_jobless': floatify(declaration.income['12']['family']),
            'alimony': floatify(declaration.income['13']['value']),
            'f_alimony': floatify(declaration.income['13']['family']),
            'heritage': floatify(declaration.income['14']['value']),
            'f_heritage': floatify(declaration.income['14']['family']),
            'insurance': floatify(declaration.income['15']['value']),
            'f_insurance': floatify(declaration.income['15']['family']),
            'sold': floatify(declaration.income['16']['value']),
            'f_sold': floatify(declaration.income['16']['family']),
            'business': floatify(declaration.income['17']['value']),
            'f_business': floatify(declaration.income['17']['family']),
            'invest': floatify(declaration.income['18']['value']),
            'f_invest': floatify(declaration.income['18']['family']),
            'rent': floatify(declaration.income['19']['value']),
            'f_rent': floatify(declaration.income['19']['family']),
            'other': floatify(declaration.income['20']['value']),
            'f_other': floatify(declaration.income['20']['family']),
            'foreign': sum(map(lambda x: floatify(x['uah_equal']), declaration.income['21'])),
            'foreign_country': ';'.join(map(lambda x: x['country'], declaration.income['21'])),
            'f_foreign': sum(map(lambda x: floatify(x['uah_equal']), declaration.income['22'])),
            'f_foreign_country': ';'.join(map(lambda x: x['country'], declaration.income['22'])),
            'earth_space': sum(estate_space(declaration.estate['23'])),
            'earth_space_num': len(estate_space(declaration.estate['23'])),
            'f_earth_space': sum(estate_space(declaration.estate['29'])),
            'f_earth_space_num': len(estate_space(declaration.estate['29'])),
            'house_space': sum(estate_space(declaration.estate['24'])),
            'house_space_num': len(estate_space(declaration.estate['24'])),
            'f_house_space': sum(estate_space(declaration.estate['30'])),
            'f_house_space_num': len(estate_space(declaration.estate['30'])),
            'flat_space': sum(estate_space(declaration.estate['25'])),
            'flat_space_num': len(estate_space(declaration.estate['25'])),
            'f_flat_space': sum(estate_space(declaration.estate['31'])),
            'f_flat_space_num': len(estate_space(declaration.estate['31'])),
            'cottage_space': sum(estate_space(declaration.estate['26'])),
            'cottage_space_num': len(estate_space(declaration.estate['26'])),
            'f_cottage_space': sum(estate_space(declaration.estate['32'])),
            'f_cottage_space_num': len(estate_space(declaration.estate['32'])),
            'garage_space': sum(estate_space(declaration.estate['27'])),
            'garage_space_num': len(estate_space(declaration.estate['27'])),
            'f_garage_space': sum(estate_space(declaration.estate['33'])),
            'f_garage_space_num': len(estate_space(declaration.estate['33'])),
            'other_space': sum(estate_space(declaration.estate['28'])),
            'other_space_num': len(estate_space(declaration.estate['28'])),
            'f_other_space': sum(estate_space(declaration.estate['34'])),
            'f_other_space_num': len(estate_space(declaration.estate['34'])),
            'auto': ';'.join(map(lambda x: x['brand'], declaration.vehicle['35'])),
            'auto_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['35'])),
            'auto_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['35'])))),
            'f_auto': ';'.join(map(lambda x: x['brand'], declaration.vehicle['40'])),
            'f_auto_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['40'])),
            'f_auto_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['40'])))),
            'truck': ';'.join(map(lambda x: x['brand'], declaration.vehicle['36'])),
            'truck_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['36'])),
            'truck_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['36'])))),
            'f_truck': ';'.join(map(lambda x: x['brand'], declaration.vehicle['41'])),
            'f_truck_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['41'])),
            'f_truck_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['41'])))),
            'boat': ';'.join(map(lambda x: x['brand'], declaration.vehicle['37'])),
            'boat_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['37'])),
            'boat_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['37'])))),
            'f_boat': ';'.join(map(lambda x: x['brand'], declaration.vehicle['42'])),
            'f_boat_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['42'])),
            'f_boat_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['42'])))),
            'plane': ';'.join(map(lambda x: x['brand'], declaration.vehicle['38'])),
            'plane_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['38'])),
            'plane_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['38'])))),
            'f_plane': ';'.join(map(lambda x: x['brand'], declaration.vehicle['43'])),
            'f_plane_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['43'])),
            'f_plane_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['43'])))),
            'other_vehicle': ';'.join(map(lambda x: x['brand'], declaration.vehicle['39'])),
            'other_vehicle_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['39'])),
            'other_vehicle_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['39'])))),
            'f_other_vehicle': ';'.join(map(lambda x: x['brand'], declaration.vehicle['44'])),
            'f_other_vehicle_year': ';'.join(map(lambda x: x['year'], declaration.vehicle['44'])),
            'f_other_vehicle_num': len(list(filter(None, map(lambda x: x['brand'], declaration.vehicle['44'])))),
            'bank_uah': floatify(declaration.banks['45'][0]['sum']),
            'bank_usd': floatify(declaration.banks['45'][1]['sum']),
            'bank_eur': floatify(declaration.banks['45'][2]['sum']),
            'f_bank_uah': floatify(declaration.banks['51'][0]['sum']),
            'f_bank_usd': floatify(declaration.banks['51'][1]['sum']),
            'f_bank_eur': floatify(declaration.banks['51'][2]['sum']),
        }

    def _run_knitr(self, table, fragment_only=True):
        """Runs knitr reporting script with an R table data frame and returns plain HTML string."""
        knitr_bootstrap = importr('knitrBootstrap')
        robjects.globalenv['data'] = table
        # The ugly part. Although knitr can accept a script text and return the rendering as a string, knitrBootstrap
        # doesn't respect that. Hence all the dancing with a temporary file.
        output_fd, output_path = tempfile.mkstemp(suffix='.html', text=True)
        knitr_bootstrap.knit_bootstrap(input=KNITR_SCRIPT_PATH, output=output_path, quiet=True, boot_style='flatly',
                                       code_style='sunburst',
                                       title=settings.ANALYTICS_TITLE,
                                       **{'fragment.only': fragment_only})
        with open(output_fd, 'r', encoding='utf-8') as output_file:
            output = output_file.read()

        os.remove(output_path)
        return output
