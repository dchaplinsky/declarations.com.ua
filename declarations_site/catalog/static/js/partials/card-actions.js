(function($) {
  $(function() {
    var cardActionBlock = $('.card-actions');

    $('.card-actions__action-link', cardActionBlock).on('click', function() {
      var parent = $(this).parents('.card-actions');
      $('.card-actions').not(parent).find('.card-actions__items').hide();
      $('.card-actions__items', parent).toggle();
    });

    $('.card-actions__action').on('click', function() {
      var self = $(this),
        details = self.find('.action-icon__details'),
        parent = self.closest('.card-actions');

      parent.find('.card-actions__items').hide();
      $('.action-icon__details').removeClass('action-icon__details--visible');

      var overflowRight = document.body.offsetWidth - (this.getBoundingClientRect().left + details.innerWidth() + 10);

      if (overflowRight < 0) {
        details[0].style.left = overflowRight + 'px';
      }

      details.addClass('action-icon__details--visible');
    });

    /*Клик вне элемента*/
    var clickEvent = (('ontouchstart' in document.documentElement) ? 'touchstart' : 'click');
    $(document).on(clickEvent, function(e) {
      var actionIcon = $(e.target).closest('.action-icon');

      if (!$(e.target).parents('.card-actions').length) {
        $('.card-actions__items', cardActionBlock).hide();
      }

      if (!actionIcon.length) {
        $('.action-icon__details').removeClass('action-icon__details--visible');
      }
    });
  });
})(jQuery);