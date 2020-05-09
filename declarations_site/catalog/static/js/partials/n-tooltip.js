(function($) {
  $(function() {
    function closeTooltips() {
      $('.n-tooltip__trigger--active').removeClass('n-tooltip__trigger--active');
    }

    $('.n-tooltip__trigger').on('click', function() {
      closeTooltips();
      $(this).toggleClass('n-tooltip__trigger--active').trigger("tooltip-shown");
    });

    $(document.body).on('click', function handleClickOutside(e) {
      if (
        !$(e.target).closest('.n-tooltip').length &&
        !$(e.target).closest('.n-tooltip__trigger--active').length
      ) {
        closeTooltips();
      }
    });
  });  
})(jQuery);