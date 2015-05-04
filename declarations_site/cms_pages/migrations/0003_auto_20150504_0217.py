# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django import VERSION as DJANGO_VERSION


def populate_static_pages(apps, schema_editor):
    RawHTMLPage = apps.get_model('cms_pages.RawHTMLPage')
    ContentType = apps.get_model('contenttypes.ContentType')
    HomePage = apps.get_model('cms_pages.HomePage')
    HomePageTopMenuLink = apps.get_model('cms_pages.HomePageTopMenuLink')

    raw_html_page_content_type, _ = ContentType.objects.get_or_create(
        model='rawhtmlpage',
        app_label='cms_pages',
        defaults={'name': 'rawhtmlpage'} if DJANGO_VERSION < (1, 8) else {}
    )

    home_page = HomePage.objects.all()[0]

    # Create about page
    about_page = RawHTMLPage.objects.create(
        title="Декларації: Про проект",
        slug='about',
        content_type=raw_html_page_content_type,
        path='000100010001',
        depth=3,
        numchild=0,
        body="""
<p>Вас вітає проект Канцелярської сотні — «Декларації». Це – наймасштабніша в Україні спроба електронізувати декларації чиновників, та зробити їх легкодоступними для аналізу.</p>
<p>Як це працює і навіщо потрібно?</p>
<p>Новий антикорупційний закон зобов’язує усіх чиновників, суддів, прокурорів, депутатів – всіх «державних людей» - заповнити та оприлюднити декларацію про доходи.  Новий люстраційний закон зобов’язує оприлюднити таку декларацію і всіх кандидатів на посади. За приблизними підрахунками декларації заповнять і оприлюднять близько мільйона людей.</p>
<p>І що? А нічого.</p>
<p>Тому що ця публікація буде у формі викладеного файлу зі сканом паперової декларації, заповненої від руки. І ці декларації будуть лежати на безліччі сайтів у непримітних розділах. Навіть переглянути їх важко, не кажучи про аналіз.</p>
<p>Ініціатива Канцелярська сотня прагне оцифрувати ці декларації, а також декларації попередні років. По-справжньому оцифрувати. Щоб можна було робити автоматичну аналітику, рейтинги, побачити динаміку зростання чиновницьких статків.</p>
<p>Ми просимо вас долучитись до цієї роботи. Адже Канцелярська сотня – це ви.</p>
<p>За три місяці наша група проаналізувала кілька тисяч декларацій. Ми розробили зручну електронну анкету, з перевіркою та підказками. Допомогти дуже просто. Витратьте 15 хвилин, пройдіть за посиланням та внесіть інформацію з паперової декларації у форму.</p>
<p>Ваша робота  безцінна для контролю за чиновниками. Окрім цього гарантуємо багато вражень від їхніх декларацій.</p>
<p>Також, якщо у вас є змога, можете допомогти проекту грошима, жодних сторонніх джерел фінансування у нього немає. Моя картка 5168 7423 3713 2520 (ПриватБанк).</p>
<p><br />З вдячністю, ініціативна група Канцелярської сотні.</p>

<p class="text-right"><em>У розробці проекту брали участь: Денис Бігус, Дмитро Чаплинський, Ольга Макарова, Артем Глувчинський,<br/> Дмитро Нечипоренко, Андрій Турик, Дмитро Гамбаль, Гліб Козак, Володимир Гоцик, Олександр Ботезату</em></p>
<p class="text-right"><em>Автори висловлюють вдячність Громадському люстраційному комітету за допомогу у зборі декларацій</em></p>
        """,
        url_path='/home/about/',
    )

    # Create API page
    api_page = RawHTMLPage.objects.create(
        title="Декларації: Відкритий API",
        slug='api',
        content_type=raw_html_page_content_type,
        path='000100010002',
        depth=3,
        numchild=0,
        body="""
<p>Проект «Декларації» надає доступ до всіх наявних даних у машинозчитуваному форматі JSON за допомогою простого відкритого API.</p>
<p>Для доступу до даних у форматі JSON достатньо додати параметр адресної строки "format=json" до майже будь-якої сторінки.</p>
<p>Наразі через відкритий API доступні такі URL:</p>
<ul>
    <li>Всі регіони - <a href="http://declarations.com.ua/region?format=json">http://declarations.com.ua/region?format=json</a></li>
    <li>Посади за регіоном - http://declarations.com.ua/region/&lt;регіон&gt;?format=json (наприклад, <a href="http://declarations.com.ua/region/Загальнодержавний?format=json">http://declarations.com.ua/region/Загальнодержавний?format=json</a>)</li>
    <li>Декларації за регіоном та відомством - http://declarations.com.ua/region/&lt;регіон&gt;/&lt;відомство&gt;?format=json&amp;page=&lt;номер сторінки&gt; (наприклад, <a href="http://declarations.com.ua/region/Загальнодержавний/Міністерство юстиції?format=json&amp;page=2">http://declarations.com.ua/region/Загальнодержавний/Міністерство юстиції?format=json&amp;page=2</a>)</li>
    <li>Декларації за відомством, незалежно від регіону - http://declarations.com.ua/office/&lt;відомство&gt;?format=json&amp;page=&lt;номер сторінки&gt; (наприклад, <a href="http://declarations.com.ua/office/Міністерство юстиції?format=json&amp;page=2">http://declarations.com.ua/office/Міністерство юстиції?format=json&amp;page=2</a>)</li>
    <li>Довільний пошук - http://declarations.com.ua/search?q=&lt;пошуковий запит&gt;&amp;format=json&amp;page=&lt;номер сторінки&gt; (наприклад, <a href="http://declarations.com.ua/search?q=Суддя&amp;format=json&amp;page=2">http://declarations.com.ua/search?q=Суддя&amp;format=json&amp;page=2</a>)</li>
    <li>Окрема декларація - http://declarations.com.ua/declaration/&lt;ID декларації&gt;?format=json (наприклад, <a href="http://declarations.com.ua/declaration/5257?format=json">http://declarations.com.ua/declaration/5257?format=json</a>)</li>
</ul>
<p>В тих випадках, де наявний параметр адресної строки "page", у результатах використовується нумерація сторінок для скорочення кількості даних, що передаються.</p>
<p>Інформація щодо нумерації доступна за ключем "paginator" у словнику з ключем "results". Наприклад:
<pre>"paginator": {"per_page": 30, "count": 1139, "num_pages": 38}</pre></p>
<p>Це означає що за даним запитом існує 1139 декларацій, розподілених на 38 сторінок по 30 декларацій на одну сторінку. Нумерація починається з одиниці.</p>
<p>Якщо у такому запиті не вказати параметр "page", то будуть передані результати для першої сторінки.</p>
<p>Повну схему даних окремої декларації можна подивитись у <a href="https://github.com/dchaplinsky/declarations.com.ua/blob/master/declarations_site/catalog/data/mapping_defs.json">відкритому сховищі проекту на GitHub.</a></p>
<p>Також можете ознайомитися з <a href="https://gist.github.com/dchaplinsky/ce215a4c5b7ccef24c35">прикладом програми на python</a>, що використовує API щоб завантажити та зберегти усі декларації з сайту (потребує бібліотеки requests):</p>
<script src="https://gist.github.com/dchaplinsky/ce215a4c5b7ccef24c35.js"></script>
        """,
        url_path='/home/api/',
    )

    HomePageTopMenuLink.objects.create(
        caption="Головна",
        link_external="/",
        sort_order=0,
        page_id=home_page.id
    )

    HomePageTopMenuLink.objects.create(
        caption="Регіони",
        link_external="/region",
        sort_order=1,
        page_id=home_page.id
    )

    HomePageTopMenuLink.objects.create(
        caption="Розшукуємо декларації",
        link_external="http://goo.gl/forms/OTbHz2FVbj",
        sort_order=2,
        page_id=home_page.id
    )

    HomePageTopMenuLink.objects.create(
        caption="Про проект",
        link_page_id=about_page.id,
        sort_order=3,
        page_id=home_page.id
    )

    HomePageTopMenuLink.objects.create(
        caption="Відкритий API",
        link_page_id=api_page.id,
        sort_order=4,
        page_id=home_page.id
    )

    home_page.depth = 2
    home_page.numchild = 2
    home_page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms_pages', '0002_auto_20150504_0206'),
    ]

    operations = [
        migrations.RunPython(populate_static_pages),
    ]
