(function($) {
  $(function() {
    $('.body--yc-option-d .youcontrol-tooltip__trigger').tooltipster({
      interactive: true,
      contentCloning: true,
      trigger: 'custom',
      triggerOpen: {
        mouseenter: true,
        tap: true
      },
      triggerClose: {
        mouseleave: true,
        click: true,
        scroll: true,
        tap: true
      },
      functionInit: function(instance, helper) {
        var content = $(helper.origin).siblings('div').find('.youcontrol-tooltip__contents');
        instance.content(content);
    }
    });
  });

})(jQuery);