(function($) {
  $(function() {
    $('.analytics-tabs__tab').on('click', function(e) {
      e.preventDefault();
      var $this = $(this),
        anchor = $(this).find('.analytics-tabs__tab-name'),
        iframeSrc = anchor.data('iframe-src'),
        iframesContainer = $('.analytics-page__iframe'),
        currentIframe = iframesContainer.find('[src="' + iframeSrc + '"]');

      $this.parents('.analytics-tabs').find('.analytics-tabs__tab').removeClass('analytics-tabs__tab--active');
      $this.addClass('analytics-tabs__tab--active');

      iframesContainer.find('iframe').hide();

      if (currentIframe.length) {
        currentIframe.show();
      } else {
        iframesContainer.append($('<iframe/>').attr('src', iframeSrc));
      }
    });
  });
})(jQuery);
