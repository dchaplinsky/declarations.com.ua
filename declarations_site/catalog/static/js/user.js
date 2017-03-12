$(function() {
    var login_arg_name = 'login_to=',
        username_key = 'cached_user',
        username_html, location_href;

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
            href = escape(href);
        $('#login-modal #signin a').each(function () {
            this.href = this.href.replace(/next=[^&]+/, 'next=' + href);
        });
    }

    function showLoginModal() {
        var href = window.location.href,
            pos = href.search(login_arg_name);
        if (pos > 0)
            href = href.substr(pos + login_arg_name.length);
        setLoginNext(href);
        $('#login-modal').modal('show');
    }

    function userIsAuthenticated(menu) {
        $('#login-button').html(menu);

        $('#logout').click(function () {
            if (username_key)
                localStorage.removeItem(username_key);
        });

        $('#save-search').click(function (e) {
            $(document.body).addClass('wait')
                .css({'cursor' : 'wait'});
            $('#wait-modal').modal('show');
        });

        if (username_key)
            localStorage.setItem(username_key, $('#profile').html());
    }

    function userNotAuthenticated() {
        var ss = $('#save-search');
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

    // submit search form on enter (fix typeahead)
    $('#search-form').on('keydown', function(e) {
        if (e.keyCode == 13) {
            var ta = $(this).data('typeahead'),
                val = ta.$menu.find('.active').data('value');
            if (val)
                $('#search-form').val(val);
            $('#front-searchbox form').submit();
        }
    });

    location_href = window.location.pathname + window.location.search;

    // get user menu via ajax
    $.ajax({
        url: '/user/login-menu/?next=' + escape(location_href),
    }).done(function (data) {
        if (data.search('logout') > 0) {
            userIsAuthenticated(data, username_key);
        } else {
            userNotAuthenticated(username_key);
        }
    });

    if (window.location.href.search(login_arg_name) > 0)
        setTimeout(showLoginModal, 500);
});
