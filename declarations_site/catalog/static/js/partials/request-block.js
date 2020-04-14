(function($) {

  $(function() {

    $('.request-row__close').on('click', function() {
      $(this).parents('.request-row').remove();
    });

  });

})(jQuery);