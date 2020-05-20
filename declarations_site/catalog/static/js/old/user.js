$(function() {
    var login_arg_name = 'login_to=',
        login_err_name = 'login_error',
        username_key = 'cached_user',
        username_html;

    try {
        username_html = localStorage.getItem(username_key);
    } catch(err) {
        username_key = false;
    }

    // use cached username for login-button
    if (username_html)
        $('#profile').html(username_html);

    function setLoginNext(href) {
        if (href && href.search(/\?/) > 0)
            href = encodeURI(href);
        $('#login-modal #signin a').each(function () {
            this.href = this.href.replace(/next=[^&]+/, 'next=' + href);
        });
    }

    function showLoginModal() {
        var href = window.location.href,
            pos = href.search(login_arg_name);
        if (pos > 0)
            href = href.substr(pos + login_arg_name.length);
        if (href.search(login_err_name) > 0)
            href = href.replace(login_err_name, '');
        setLoginNext(href);
        $('#login-modal').modal('show');
    }

    function showLoginErrorModal() {
        $('#login-error-modal').modal('show');
    }

    function userIsAuthenticated(menu) {
        $('#login-button').html(menu);

        $('#logout').click(function (e) {
            if (ga)
                ga('send', 'event', 'user-logout', e.target.className);
            if (username_key)
                localStorage.removeItem(username_key);
        });

        $('.save-search').click(function (e) {
            $(document.body).addClass('wait')
                .css({'cursor' : 'wait'});
            $('#wait-modal').modal('show');
        });

        if (username_key)
            localStorage.setItem(username_key, $('#profile').html());
    }

    function userNotAuthenticated() {
        var ss = $('a.save-search');
        if (ss.length) {
            setLoginNext(ss.attr('href'));
            ss.click(function (e) {
                e.preventDefault();
                $('#login-modal').modal('show');
            });
        }
        if (username_key && localStorage.getItem(username_key))
            localStorage.removeItem(username_key);
    }

    function addMultiQueries() {
        var text = $('#add-multi-modal #queries').val(),
            queries = $.trim(text).split(/[\r\n]/),
            max_queries = 50, counter = 0;

        if (queries.length < 1) {
            $('#queries-error').html('Нема чого додавати.');
            return
        }
        if (queries.length > max_queries) {
            $('#queries-error').html('Забагато запитів, максимум ' + max_queries);
            return
        }
        $('#queries-error').html('');

        var save_url = $('#add-multi').data('href');

        function do_ajax() {
            if (counter >= queries.length) {
                location.reload();
                return;
            }

            var q = $.trim(queries[counter]),
                ajax_url = save_url + '?q=' + encodeURI(q);

            if (q.length < 3 || q.length > 100) {
                counter += 1;
                return do_ajax();
            }

            $.ajax({
                url: ajax_url,
                success: function () {
                    counter += 1;
                    var ps = 100 * counter / queries.length;
                    $('.add-progress .progress-bar').css('width', ps+'%');
                    do_ajax();
                },
                error: function () {
                    $('.add-progress').html('Виникла помилка :(');
                    setTimeout(function() {
                        location.reload();
                    }, 3000);
                }
            });
        }

        $('#add-multi-modal .add-form').hide();
        $('#add-multi-modal .modal-footer').hide();
        $('#add-multi-modal .add-progress').show();

        do_ajax();
    }

    $('#add-multi-btn').on('click', function (e){
        addMultiQueries();
    });

    $('#add-multi-modal').on('show.bs.modal', function (e) {
        $('#add-multi-modal .add-progress').hide();
        $('#add-multi-modal .modal-footer').show();
        $('#add-multi-modal .add-form').show();
        $('#add-multi-modal #queries').val('');
        $('#add-multi-modal #queries-error').html('');
    });

    $('.signin-menu a').on('click', function (e) {
        ga('send', 'event', 'user-login', e.target.className);
    });

    $('a.save-search').on('click', function (e) {
        ga('send', 'event', 'save-search', $(e.target).data('from'));
    });

    $('#login-modal').on('shown.bs.modal', function (e) {
        var href = $(e.relatedTarget).data('href');
        if (href)
        	setLoginNext(href);
    });

    $('#login-email-modal').on('hidden.bs.modal', function (e) {
        $('#login-modal-email-form').show();
        $("#login-modal-success-message").hide();
        $('#login-email-input').val("").prop("disabled", false);
    });

    $('#btn-send-login-email').on('click', function (e) {
        email = $('#login-email-input').val();
        if (!email)
            return
        $('#login-email-input').prop("disabled", true);
        $.post(
            '/user/send-login-email/', {email: encodeURI(email)}
        ).done(function (data) {
            $('#login-modal-email-form').hide();
            $("#login-modal-success-message").show();
            $('#login-email-input').prop("disabled", false);
        }).fail(function () {
            $('#login-email-modal').modal('hide');
            setTimeout(showLoginErrorModal, 500);
        });
    });

    $('#search-list .delete').click(function (e) {
        if (!confirm('Точно видалити?')) {
            e.preventDefault();
        }
    });

    $('#show-login-modal').click(function () {
        $('#login-error-modal').modal('hide');
        setTimeout(showLoginModal, 500);
    });

    var full_path = window.location.pathname + window.location.search;

    // get user menu via ajax
    $.ajax({
        url: ($("#login-button").data("url") || '/user/login-menu/') + "?next=" + encodeURI(full_path),
    }).done(function (data) {
        if (data.search('logout') > 0) {
            userIsAuthenticated(data, username_key);
        } else {
            userNotAuthenticated(username_key);
        }
    });

    if (full_path.search(login_arg_name) > 0)
        setTimeout(showLoginModal, 500);
    else if (full_path.search(login_err_name) > 0)
       setTimeout(showLoginErrorModal, 500);
});
