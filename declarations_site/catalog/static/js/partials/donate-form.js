(function($) {

  $(function() {

    addEventOnRequestBlock();

    var donateBtn = document.getElementsByClassName('donation-btn');

    if(donateBtn) {

      for(var i=0; i<donateBtn.length; i++) {

        donateBtn[i].addEventListener('popupLoad', function() {
          addEventOnRequestBlock();
        });

      }

    }

    function addEventOnRequestBlock(){

      var donateForm = $('.donate-form');

      $('.donate-form__price-btn', donateForm).on('click', function() {
        var $this = $(this);
        $('.donate-form__price-btn', donateForm).removeClass('active');
        $this.addClass('active');
        $('.donate-form__input', donateForm).val($this.data('price'));
      });

    }


  });

})(jQuery);