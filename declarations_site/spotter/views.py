from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from functools import partial

from catalog.utils import replace_apostrophes
from spotter.models import SearchTask
from spotter.utils import first_run, send_newtask_notify


login_required = partial(login_required, redirect_field_name='login_to', login_url='/')


def silent_logout(request):
    logout(request)
    return redirect(request.GET.get('next', settings.LOGOUT_REDIRECT or '/'))


def login_menu(request, template_name='login_menu.jinja'):
    if not request.user.is_authenticated:
        return HttpResponse('')
    path = request.GET.get('next', '')
    return render(request, template_name, {'path': path})


@login_required
def search_list(request, template_name='search_list.jinja'):
    task_list = SearchTask.objects.filter(user=request.user,
        is_deleted=False).defer('found_ids').order_by('-created')
    return render(request, template_name, {'task_list': task_list})


@login_required
def save_search(request):
    query = replace_apostrophes(request.GET.get("q", "")).strip()
    deepsearch = bool(request.GET.get("deepsearch", ""))

    if len(query) < 2:
        messages.warning(request, 'Не вдалось створити завдання з пустим запитом.')
        return redirect('search_list')

    if not request.user.email:
        messages.warning(request, 'Не вдалось створити завдання без адреси електронної пошти.')
        return redirect('search_list')

    # don't add twice
    if SearchTask.objects.filter(user=request.user,
            query=query, deepsearch=deepsearch, is_deleted=False).exists():
        messages.warning(request, 'Таке завдання вже існує.')
        return redirect('search_list')

    task = SearchTask(user=request.user, query=query, deepsearch=deepsearch)
    task.save()

    first_run(task)
    if not send_newtask_notify(task):
        messages.warning(request, 'Не вдалось відправити лист на адресу %s' % task.user.email)

    messages.success(request, 'Завдання "%s" створено.' % task.query)
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
