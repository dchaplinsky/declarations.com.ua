from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from social_django.models import DjangoStorage
from functools import partial

from catalog.utils import replace_apostrophes
from spotter.models import SearchTask
from spotter.forms import UserProfileForm
from spotter.utils import (first_run, send_newtask_notify, send_confirm_email,
    get_verified_email, reverse_qs, get_email_login_userid, send_login_temporary_link)


login_required = partial(login_required, redirect_field_name='login_to', login_url='/')


def silent_logout(request):
    logout(request)
    return redirect(request.GET.get('next', settings.LOGOUT_REDIRECT or '/'))


def login_menu(request, template_name='login_menu.jinja'):
    if not request.user.is_authenticated:
        return HttpResponse('')
    path = request.GET.get('next', '')
    return render(request, template_name, {'path': path})


def login_via_email(request):
    user_id = get_email_login_userid(request)
    email = request.GET.get('email', '')
    if not user_id:
        return redirect(settings.SOCIAL_AUTH_LOGIN_ERROR_URL)
    user = DjangoStorage.user.get_user(user_id, email=email)
    if not user or not user.is_active:
        return redirect(settings.SOCIAL_AUTH_LOGIN_ERROR_URL)
    if request.user and request.user.is_authenticated:
        logout(request)
    backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user, backend=backend)
    return redirect('search_list')


@csrf_exempt
@require_POST
def deauthorize(request):
    return HttpResponse('OK')


@csrf_exempt
@require_POST
def send_login_email(request):
    email = request.POST.get('email', '-')
    try:
        validate_email(email)
    except ValidationError:
        raise Http404("Bad E-mail")

    for user in DjangoStorage.user.get_users_by_email(email):
        if user.is_active:
            send_login_temporary_link(user.id, email)

    if request.is_ajax():
        return HttpResponse('OK')

    return redirect('/')


@login_required
def search_list(request, template_name='search_list.jinja'):
    task_list = SearchTask.objects.filter(user=request.user,
        is_deleted=False).defer('found_ids').order_by('-created')
    return render(request, template_name, {'task_list': task_list})


def do_save_search(request, query, deepsearch, query_params):
    if len(query) < 2 and len(query_params or '') < 15:
        messages.warning(request, 'Не вдалось створити завдання з пустим запитом.')
        return redirect('search_list')

    if len(query) > 100 or len(query.split(' ')) > 10:
        messages.warning(request, 'Не вдалось створити завдання з таким довгим запитом.')
        return redirect('search_list')

    if not request.user.is_active:
        messages.warning(request, 'Не вдалось створити завдання. Користувача заблоковано.')
        return redirect('logout')

    if not request.user.email:
        messages.warning(request, 'Не вдалось створити завдання без адреси електронної пошти. ' +
            'Спочатку введіть адресу.')
        return redirect(reverse_qs('edit_email', qs={'next': request.get_full_path()}))

    if SearchTask.objects.filter(user=request.user,
                                 is_deleted=False).count() >= settings.SPOTTER_TASK_LIMIT:
        messages.warning(request, 'Перевищено максимальну кількість завдань.')
        return redirect('search_list')

    # don't add twice
    if SearchTask.objects.filter(user=request.user, query=query,
            deepsearch=deepsearch, query_params=query_params, is_deleted=False).exists():
        messages.warning(request, 'Таке завдання вже існує.')
        return redirect('search_list')

    task = SearchTask(user=request.user, query=query, deepsearch=deepsearch)
    task.query_params = query_params

    # we need chat_data for create chatbot task
    if request.user.email and request.user.email.endswith(".chatbot"):
        prev_task = SearchTask.objects.filter(user=request.user)
        if not prev_task.exists():
            messages.warning(request, 'Для початку створіть хоч одне завдання з чату.')
            return redirect('search_list')
        task.chat_data = prev_task[0].chat_data

    task.save()

    if not first_run(task):
        messages.warning(request, 'Не вдалось створити завдання, спробуйте спростити ' +
                         'запит "%s"' % task.query)
        task.is_deleted = True
        task.save()
        return redirect('search_list')

    elif not send_newtask_notify(task):
        messages.warning(request, 'Не вдалось відправити лист на адресу %s' % task.user.email)

    if not request.is_ajax():
        messages.success(request, 'Завдання "%s" створено.' % task.query)

    return redirect('search_list')


@login_required
def save_search(request):
    query = replace_apostrophes(request.GET.get("q", "")).strip()
    deepsearch = bool(request.GET.get("deepsearch", ""))

    params = request.GET.copy()
    for key in ("q", "deepsearch", "format", "page", "sort"):
        if key in params:
            params.pop(key)

    response = do_save_search(request, query, deepsearch, params.urlencode())

    if request.is_ajax():
        return HttpResponse('OK')

    return response


@login_required
def edit_email(request, template_name='edit_email.jinja'):
    if request.user.email and request.user.email.endswith(".chatbot"):
        messages.warning(request, 'Неможливо змінити адресу')
        return redirect('search_list')

    form = UserProfileForm(request.POST or None,
        initial={'email': request.user.email})

    if request.POST and form.is_valid():
        email = form.cleaned_data['email']
        if send_confirm_email(request, email):
            messages.success(request, 'На вказану адресу відправлено лист. ' +
                'Будь ласка перейдіть за посиланням в листі для підтвердження адреси.')
        else:
            messages.warning(request, 'Не вдалось відправити лист на адресу %s' % email)

    return render(request, template_name, {'form': form})


@login_required
def confirm_email(request):
    email = get_verified_email(request)
    if email:
        request.user.email = email
        request.user.save()
        messages.success(request, 'Адресу %s підтверджено.' % email)
    else:
        messages.warning(request, 'Не вдалось підтвердити адресу.')
    return redirect('search_list')


@require_POST
@login_required
def edit_search(request, task_id):
    task = get_object_or_404(SearchTask, id=task_id, user=request.user, is_deleted=False)
    action = request.POST['action']
    if action == 'enable':
        task.is_enabled = True
        msg = 'відновлено'
    elif action == 'disable':
        task.is_enabled = False
        msg = 'призупинено'
    elif action == 'delete':
        task.is_enabled = False
        task.is_deleted = True
        msg = 'видалено'
    else:
        msg = 'не змінено'
    task.save()
    messages.success(request, 'Завдання "%s" %s.' % (task.query, msg))
    return redirect('search_list')
