/* run scripts when document is ready */
$(function() {
  "use strict";

  var $window = $(window);
  var $body = $(document.body);
  var analytics_wrapper = $body.find('.analytics-wrapper');

  /* size of thumbnails */
  var thumbsize = "col-md-3";

  /* Using render_html, so add in code block */
  analytics_wrapper.find('pre.knitr').each(function(){
    $(this).removeClass('knitr');
    if($(this).find('code').length < 1){
      $(this).wrapInner('<code class=' + $(this).attr('class') + '></code>');
    }
  });

  /* style tables */
  analytics_wrapper.find('table').addClass('table table-striped table-bordered table-hover table-condensed');

  /* give images a lightbox and thumbnail classes to allow lightbox and thumbnails TODO: make gallery if graphs are grouped */
  analytics_wrapper.find('div.rimage img').each(function(){

    //remove rimage div
    $(this).unwrap();

    var a = $(this).
      wrap('<a href=# class="media-object pull-left mfp-image thumbnail ' + thumbsize + '"></a>').
      parent();

    var sibs = a.prevUntil('div.rimage,div.media');
    var div = $('<div class="media" />');
    if(sibs.length != 0){
      sibs.addClass('media-body');
      //need to reverse order as prevUntil puts objects in the order it found them
      $(sibs.get().reverse()).wrapAll(div).parent().prepend(a);
    }
    else {
      a.wrap(div);
    }
  });

  analytics_wrapper.find('div.chunk').addClass('media');

  /* Magnific Popup */
  analytics_wrapper.find(".thumbnail").each(function(){
    $(this).magnificPopup({
      disableOn: 768,
      closeOnContentClick: true,

      type: 'image',
      items: {
        src: $(this).find('img').attr('src'),
      }
    });
  });

  /* remove paragraphs with no content */
  $('p:empty').remove();
});