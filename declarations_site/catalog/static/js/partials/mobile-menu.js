(function($) {

  $(function() {

    let vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');

    let menuBtn = $('.mobile-menu-link');
    let mobileMenu = $('.mobile-menu');
    let body = $('body');

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