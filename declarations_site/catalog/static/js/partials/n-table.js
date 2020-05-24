(function($) {
  $(function() {
    $('.n-table__collapsable').on('click', function toggle() {
      $(this).toggleClass('n-table__collapsable--expanded');
    });
  });
})(jQuery);