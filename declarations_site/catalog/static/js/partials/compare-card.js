(function($) {

  $(function() {

    $('.compare-card__dropdown').on('click', function() {
      let $this = $(this);
      $this.toggleClass('drop-down-btn_opened');
      $this.parents('.compare-card').toggleClass('compare-card_opened');
    });

  });

})(jQuery);