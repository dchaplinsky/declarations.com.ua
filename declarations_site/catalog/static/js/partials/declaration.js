(function($) {

    $(function() {
  
      var Contents = function (contentBlock) {
  
        this.contents = $('.contents');
  
        self = this;
  
        generateContentsItems(contentBlock);
        addEvents();
  
  
        function generateContentsItems(contentBlock) {
          setIdForTitles(contentBlock);
          var links = '';
          contentBlock.each(function() {
            var $this = $(this);
            var idBlock = '#' + $this.attr('id');
            var linkClass = 'contents__item ' + $this.data('empty');
            links += '<a class="' + linkClass + '" href="' + idBlock + '">' + $('h2', $this).html() + '</a>';
          });
          $('.contents__items', self.contents).append(links);
        }
  
        function setIdForTitles(contentBlock) {
          var counter = 1;
          contentBlock.each(function() {
            $(this).attr('id', 'declaration-title-' + counter);
            counter += 1;
          });
        }
  
        function closeContents() {
          self.contents.removeClass('opened');
          $('html').removeClass('contents-lock');
        }
  
        function addEvents() {
  
          $('.contents__close', self.contents).on('click', function() {
            closeContents();
          });
  
          $('.contents__open', self.contents).on('click', function() {
            self.contents.addClass('opened');
            $('html').addClass('contents-lock');
          });
  
          $('.contents__item', self.contents).on('click', function(e) {
            e.preventDefault();
            var scrollBlock = $(this).attr('href');
            scrollBlock = $(scrollBlock);
            closeContents();
            $('.nacp-section').removeClass('opened');
            $('html, body').animate({
              scrollTop: scrollBlock.offset().top
            }, 1000, 'swing', function() {
              scrollBlock.addClass('opened');
            });
          });
  
        }
  
      };
  
  
      var declarationBlock = $('.declaration-details');
  
      if (declarationBlock.length) {
        prepareContent(declarationBlock.data('page-type') || 1);
        addEvents();
        new Contents($('.content-section'));
      }
  
      function prepareContent(declarationType) {
        if(declarationType === 1) {
          prepareContentType1();
        }
        else {
          prepareContentType2()
        }
      }
  
      function prepareContentType2(){
        $('table', declarationBlock).wrap('<div class="table-responsive"></div>');
        $('.weiss-form__set_main', declarationBlock).addClass('content-section');
        $('.weiss-form__set_main', declarationBlock).attr('data-empty', 'full');
      }
  
      function prepareContentType1(){
  
        var declaration = $('.declaration-details');
  
        declaration.contents().filter(function() {
          return this.nodeType === 3; // get only the text nodes
        })
        .wrap( "<p></p>" );
  
  
        $('header', declaration).each(function(){
          $(this).nextUntil("header").addBack().wrapAll('<div class="nacp-section content-section" />');
        });
  
  
        $('.nacp-section').each(function( index ) {
  
          var $this = $(this);
          var someInfo = $this.find('table, .personal-info, label');
          var dataEmpty = someInfo.length ? 'full' : 'empty';

          if (someInfo.length) {
            $this.addClass('opened');
          }
  
          $this.find('header').children().not('h2').insertAfter($this.find('header'));
          $this.children().not('header').wrapAll('<div class="body" />');
          $this.attr('id', 'toc-id-' + index);
          $this.attr('data-empty', dataEmpty);
  
          if(index > 1 && index < 18) {
            var $body = $this.find('.body');
            $body.each(function() {
              $(this).find('p').nextUntil('div').addBack().wrapAll('<div class="help-block__text" />');
              $(this).find('.help-block__text').wrap('<div class="help-block"></div>');
              var helpText = $(this).find('.help-block');
              helpText.prepend(generateHelpBtn());
            });
          }
  
        });
  
  
      }
  
      function addEvents(){
  
        $('.help-block__btn').on('click', function() {
          $(this).next('.help-block__text').toggle();
        });
  
        $('.nacp-section header').on('click', function() {
          $(this).parents('.nacp-section').toggleClass('opened');
        });
  
      }
  
  
      $('.tenders__top').on('click', function() {
        if (window.matchMedia("(min-width: 1024px)").matches) {
          $('.tenders').toggleClass('opened');
        }
      });
  
      $('.tenders__description').on('click', function() {
        if (!window.matchMedia("(min-width: 1024px)").matches) {
          $('.tenders').toggleClass('opened');
        }
      });
  
      function downloadDeclarationContent(declarationId, callback) {
        var contentUrl = 'declaration/' + declarationId + '.html';
        jQuery.ajax({
          url: contentUrl,
          type: "get",
          data: [],
          success: function success(response, textStatus, jqXHR) {
            callback(response);
          } });
      }
  
      function generateHelpBtn(){
        var btn = '<div class="help-block__btn-dot"></div>';
        var title = 'Пояснення щодо цього розділу декларації';
        btn += '<div class="help-block__btn-dot"></div>';
        btn += '<div class="help-block__btn-dot"></div>';
        btn = '<div title="' + title + '" class="help-block__btn">' + btn + '</div>';
        return btn;
      }
  
    });
  
  })(jQuery);