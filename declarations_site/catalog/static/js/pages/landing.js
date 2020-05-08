(function($) {
  $(function() {
    $('#year').on('change', function() {
      $('.landing-page__declarants-table')
        .hide()
        .filter('#declarants-' + $(this).val())
        .show();
    });
  });
  
})(jQuery);
