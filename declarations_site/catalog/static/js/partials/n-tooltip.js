(function($) {
  $(function() {
    function closeTooltips() {
      $('.n-tooltip__trigger--active').removeClass('n-tooltip__trigger--active');
    }

    $('.n-tooltip__trigger').on('click', function(e) {
      var target = $(e.target);

      if ((target.closest('.n-tooltip').length || target.hasClass('n-tooltip__close'))) {
        return;
      }

      closeTooltips();
      $(this).toggleClass('n-tooltip__trigger--active').trigger("tooltip-shown");
    });

    $('.n-tooltip__close').on('click', closeTooltips);

    $(document.body).on('click', function handleClickOutside(e) {
      var target = $(e.target);

      if (
        (!target.closest('.n-tooltip').length || target.hasClass('n-tooltip__close')) &&
        !target.closest('.n-tooltip__trigger').length
      ) {
        closeTooltips();
      }
    });
  });  
})(jQuery);