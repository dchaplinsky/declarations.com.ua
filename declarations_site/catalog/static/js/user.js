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
        url: '/user/login-menu/?next=' + encodeURI(full_path),
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
