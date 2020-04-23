(function ($) {

  $(function () {

    var body = $('body');
    var html = $('html');

    $('.popup-btn').on('click', function (e) {

      e.preventDefault();

      var $this = $(this);
      var contentUrl = $this.attr('href');
      var popupWidth = $this.data('width');
      var popupBtn = this;

      downloadContent(contentUrl, function (response) {
        renderPopup(response, popupBtn, popupWidth);
      });
    });



    function downloadContent(contentUrl, callback) {
      var content = document.getElementById(contentUrl);
      if (!content) {
        $.ajax({
          url: contentUrl,
          type: 'get',
          data: [],
          success: function success(response, textStatus, jqXHR) {
            callback(response);
          }
        });
      } else {
        callback($(content).html());
      }
    }



    function renderPopup(content, popupBtn, popupWidth) {
      var popup = $($('#popup-template').html());
      $('.popup__content', popup).append(content);
      if(popupWidth) {
        $('.popup__wrap', popup).css('width', popupWidth);
      }
      openPopup(popup);
      var eventName = 'popupLoad';
      var event;
      if (typeof(Event) === 'function') {
        event = new Event(eventName);
        popupBtn.dispatchEvent(event);
      } else {
        event = document.createEvent('Event');
        event.initEvent("popupLoad", true, false);
        popupBtn.dispatchEvent(event);
      }
    }



    function openPopup(popup) {

      html.addClass('popup-lock');
      body.append(popup);

      $('.popup__content', popup).fadeTo(400, 1, function() {

        $('.popup__close', popup).on('click', function (e) {
          e.preventDefault();
          closePopup(popup);
        });

        popup.on('click', function(e) {
          if (window.matchMedia("(min-width: 1024px)").matches) {
            if ( !$(e.target).parents('.popup__content').length ) {
              closePopup(popup);
            }
          }

        });

      });

    }



    function closePopup(popup) {
      $('.popup__content', popup).fadeTo(400, 0, function() {
        popup.remove();
        html.removeClass('popup-lock');
      });
    }


  });

})(jQuery);