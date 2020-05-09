import io
from jmespath import compile as jc
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import DetailView
from collections import OrderedDict
import xlsxwriter

from .models import LandingPage


class LandingPageDetail(DetailView):
    model = LandingPage
    template_name = "landings/landingpage_detail.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def render_excel(self, summary):
        fields_mapping = OrderedDict(
            [
                (jc("aggregated_data.name"), "Повне ім'я"),
                (None, "Порівняти"),
                (jc("year"), "Рік подання"),
                (
                    jc("aggregated_data.name_post"),
                    "ПІБ декларанта, посада та місце роботи",
                ),
                (
                    jc("aggregated_data.organization_group"),
                    "Установа, де працює декларант",
                ),
                (
                    jc('aggregated_data."liabilities.total"'),
                    "Загальна сума зобов’язань",
                ),
                (
                    jc('aggregated_data."liabilities.total"'),
                    "Загальна сума зобов’язань",
                ),
                (jc('aggregated_data."incomes.total"'), "Загальний дохід (грн)"),
                (jc('aggregated_data."expenses.total"'), "Загальні витрати (грн)"),
                (jc('aggregated_data."assets.total"'), "Загальні статки (грн)"),
                (
                    jc('aggregated_data."vehicles.all_names"'),
                    "Назви всіх ТЗ (за наявності)",
                ),
                (jc('aggregated_data."vehicles.total_cost"'), "Загальна вартість ТЗ"),
                (jc('aggregated_data."estate.total_land"'), "Загальна площа землі, м2"),
                (
                    jc('aggregated_data."estate.total_other"'),
                    "Загальна площа нерухомості, крім землі, м2",
                ),
            ]
        )
        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)
        bold_blue = workbook.add_format({"bold": True, "color": "navy"})
        top_border = workbook.add_format({"top": True})
        url_format_top_border = workbook.add_format({"top": True, "hyperlink": True})

        worksheet = workbook.add_worksheet()
        worksheet.set_header("&Cdeclarations.com.ua — проект Канцелярської сотні")
        worksheet.freeze_panes(1, 1)
        worksheet.autofilter(0, 0, 0, 1)

        for col_num, col_title in enumerate(fields_mapping.values()):
            worksheet.write(0, col_num, col_title, bold_blue)
            worksheet.set_column(col_num, col_num, len(col_title))

        row_num = 1
        max_len_of_name = 0
        for person in summary["persons"]:
            for i, d in enumerate(person["documents"].values()):
                if i == 0:
                    worksheet.set_row(row_num, 20, top_border)

                for col_num, field in enumerate(fields_mapping.keys()):
                    if field is None:
                        if i == 0:
                            url = "https://declarations.com.ua/compare?{}".format(
                                    "&".join(
                                        "declaration_id={}".format(decl_id)
                                        for decl_id in jc("[*].infocard.id").search(
                                            list(person["documents"].values())
                                        )
                                    )
                                )

                            if len(url) < 255:
                                worksheet.write_url(
                                    row_num,
                                    col_num,
                                    url,
                                    url_format_top_border,
                                    "Порівняти",
                                )
                            else:
                                worksheet.write(
                                    row_num,
                                    col_num,
                                    " " + url,
                                    url_format_top_border,
                                )

                        continue

                    value = field.search(d)

                    if col_num == 0:
                        worksheet.write_url(
                            row_num,
                            col_num,
                            d["aggregated_data"].get("link", ""),
                            (url_format_top_border if i == 0 else None),
                            value,
                        )
                        max_len_of_name = max(max_len_of_name, len(value or ""))
                    else:
                        worksheet.write(
                            row_num, col_num, value, (top_border if i == 0 else None)
                        )

                row_num += 1

        worksheet.set_column(0, 0, max_len_of_name)
        workbook.close()

        output.seek(0)
        return output

    def render_to_response(self, context):
        if self.request.GET.get("format") == "json":
            return JsonResponse(context["object"].get_summary(), safe=False)
        if self.request.GET.get("format") == "xlsx":
            filename = "{}_declarations.xlsx".format(context["object"].slug)

            response = HttpResponse(
                self.render_excel(context["object"].get_summary()),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = "attachment; filename=%s" % filename

            return response
        else:
            context["summary"] = context["object"].get_summary()
            return super().render_to_response(context)


class LandingPagePerson(DetailView):
    model = LandingPage
    template_name = "landings/landingpage_person.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def render_to_response(self, context):
        if self.request.GET.get("format") == "json":
            return JsonResponse(context["object"].get_summary(), safe=False)

        return super().render_to_response(context)
