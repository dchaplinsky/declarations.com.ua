(function($) {
  $(function() {
    function markTabActive(tab) {
      tab.closest('.tabs')
        .find('.tabs__link').removeClass('tabs__link--active');
      tab.addClass('tabs__link--active');
    }

    function activateTab(hash) {
      var tabLink = $('.tabs__link[href="' + hash + '"]');
      
      if (tabLink.length) {
        markTabActive(tabLink);

        $('.tabs__tab').hide()
          .filter(hash).show().trigger("activated");
      }
    }

    $('.tabs__link').on('click', function(e) {
      var self = $(this),
        tabLink = self.attr('href');

      if (tabLink.indexOf('#') === 0) {
        e.preventDefault();
        activateTab(tabLink);
        history.pushState(null, null, tabLink);
      }
    });
    
    if (document.location.hash) {
      activateTab(document.location.hash);
    }

    $(window).on('popstate', function(e) {
      activateTab(document.location.hash);
    })
  });
  
})(jQuery);