(function($) {
  $(function() {
    function switchLoginSection(section) {
      $('.login-block')
        .removeClass('login-block--error login-block--email login-block--success login-block--loading')
        .addClass('login-block--' + section);
      
      if (section === 'email') {
        $('#login-email-input').focus();
      }
    }

    function setLoginNext(href) {
      if (href && href.search(/\?/) > 0)
          href = encodeURI(href);
      $('#login-modal #signin a').each(function () {
          this.href = this.href.replace(/next=[^&]+/, 'next=' + href);
      });
    }

    var loginArgName = 'login_to=',
      loginErrName = 'login_error',
      usernameKey = 'cached_user';

    function showLoginModal() {
      var href = window.location.href,
        pos = href.search(loginArgName);
      if (pos > 0)
        href = href.substr(pos + loginArgName.length);
      if (href.search(loginErrName) > 0)
        href = href.replace(loginErrName, '');
      setLoginNext(href);
      $('.account-block a').click();
    }

    function showLoginErrorModal() {
      $('.account-block a').click();
      $('.login-block').addClass('login-block--error');
    }

    $(document.body)
      .on('click', '.login-block__other', function() {
        switchLoginSection($(this).data('show'));
      })
      .on('click', '.login-block__btns a', function(e) {
        ga('send', 'event', 'user-login', e.target.className);
      })
      .on('click', '.account-block__logout', function(e) {
        if (ga) ga('send', 'event', 'user-logout', e.target.className);
      })
      .on('click', '.login-block__other--email-submit', function(e) {
        var email = $('#login-email-input').val();
  
        if (!email) return;
  
        switchLoginSection('loading');

        $('#login-email-input').prop('disabled', true);
        $.post('/user/send-login-email/', {email: encodeURI(email)})
          .done(function(data) {
            $('.login-block')
              .removeClass('login-block--loading')
              .addClass('login-block--success');
            $('#login-email-input').prop('disabled', false);
          })
          .fail(function() {
            $('.login-block').addClass('login-block--error');
          });
      });

    /*Клик вне элемента*/
    var clickEvent = (('ontouchstart' in document.documentElement)?'touchstart':'click');
    $(document).on(clickEvent, function(e){
      if ( !$(e.target).parents('.account-block').length ) {
        $('.account-block__dropdown', $('.login-block')).hide();
      }
    });
  
    var fullPath = window.location.pathname + window.location.search;

    // get user menu via ajax
    $.ajax({
      url: ($('.login-button').data('url') || '/user/login-menu/') + '?next=' + encodeURI(fullPath),
    }).done(function(data) {
      if (data.search('logout') <= 0) {
        var ss = $('a.save-search');
        if (ss.length) {
          setLoginNext(ss.attr('href'));
          ss.click(function(e) {
            e.preventDefault();
            $('.account-block a').click();
          });
        }
      }
    });

    if (fullPath.search(loginArgName) > 0)
      setTimeout(showLoginModal, 500);
    else if (fullPath.search(loginErrName) > 0)
      setTimeout(showLoginErrorModal, 500);
  });
})(jQuery);
