(function($) {
  $(function() {
    function closeTooltips() {
      $('.n-tooltip__trigger--active').removeClass('n-tooltip__trigger--active');
    }

    $('.n-tooltip__trigger').on('click', function() {
      if (window.matchMedia('(max-width: 1023px)').matches) {
        closeTooltips();
        $(this).toggleClass('n-tooltip__trigger--active');
      }
    });

    $(document.body).on('click', function() {
      if (window.matchMedia('(max-width: 1023px)').matches && !$(this).closest('.n-tooltip').length) {
        closeTooltips();
      }
    });
  });  
})(jQuery);