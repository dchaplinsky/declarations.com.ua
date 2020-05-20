(function($) {
  $(function() {
    $('.analytics-tabs__tab').on('click', function(e) {
      e.preventDefault();
      var $this = $(this),
        anchor = $(this).find('.analytics-tabs__tab-name');
      $this.parents('.analytics-tabs').find('.analytics-tabs__tab').removeClass('analytics-tabs__tab--active');
      $this.addClass('analytics-tabs__tab--active');

      $('.analytics-page__iframe iframe').attr('src', anchor.data('iframe-src'));
    });
  });
})(jQuery);
