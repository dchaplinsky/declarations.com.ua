(function($) {

  $(function() {

    var select = $('.n-select');

    $('.n-select__selected', select).on('click', function() {
      var list = $(this).parents('.n-select');
      $('.n-select__items', list).toggle();
      $('.n-select__selected', list).toggleClass('n-select__selected_active');
    });

    $('.n-select__item', select).on('click', function() {
      selectItem($(this));
    });

    /*Клик вне списка*/
    var clickEvent = (('ontouchstart' in document.documentElement)?'touchstart':'click');
    $(document).on(clickEvent, function(e){
      if ( !$(e.target).parents('.n-select').length ) {
        closeList(select);
      }
    });

    function closeList(list){
      $('.n-select__items', list).hide();
      $('.n-select__selected', list).removeClass('n-select__selected_active');
    }

    function selectItem(selectedItem) {
      var list = selectedItem.parents('.n-select');
      $('.n-select__selected', list).text(selectedItem.text());
      $('.n-select__item', list).removeClass('n-select__item_active');
      selectedItem.addClass('n-select__item_active');
      closeList(list);
    }

  });

})(jQuery);