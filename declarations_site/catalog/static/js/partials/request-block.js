(function($) {
  $(function() {
    $('.request-row__close .close-btn').click(function(e) {
      if (!confirm('Точно видалити?')) {
        e.preventDefault();
      }
    });
  });

})(jQuery);