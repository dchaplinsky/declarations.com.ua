(function($) {

  $(function() {

    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');

    var menuBtn = $('.mobile-menu-link');
    var mobileMenu = $('.mobile-menu');
    var body = $('body');

    menuBtn.on('click', function (e) {
      e.preventDefault();
      mobileMenu.addClass('mobile-menu_open');
      body.addClass('menu-is-open');
    });
    
    $('.popup-btn', mobileMenu).on('click', function() {
      setTimeout(function() {
        closeMenu();
      }, 300);
    });

    $('.mobile-menu__close-btn', mobileMenu).on('click', function (e) {
      e.preventDefault();
      closeMenu();
    });

    function closeMenu() {
      mobileMenu.removeClass('mobile-menu_open');
      body.removeClass('menu-is-open');
    }

  });

})(jQuery);