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

          function createContentsItem(selector) {
            var extraItem = $(selector);

            if (extraItem.length) {
              return '<a class="contents__item" href="' + selector + '">' + extraItem.find('span').text() + '</a>';
            }

            return '';
          }

          links += ['.declaration-card__feature', '#tenders']
            .map(createContentsItem)
            .join('');

          contentBlock.each(function() {
            var $this = $(this);
            var idBlock = '#' + $this.attr('id');
            var linkClass = 'contents__item ' + $this.data('empty');
            links += '<a class="' + linkClass + '" href="' + idBlock + '">' + $('h2', $this).html() + '</a>';
          });

          // add related blocks to TOC
          links += ['#other_wordings', '#exact_by_surname', '#similar_by_surname', '#similar_by_relations']
            .map(createContentsItem)
            .join('');

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
        prepareContent(declarationBlock.data('type') || 1);
        addEvents();
        new Contents($('.content-section'));
        replaceDeclText4Icons();
      }
  
      function prepareContent(declarationType) {
        if(declarationType === 1) {
          prepareContentType1();
        }
        else {
          prepareContentType2()
        }
      }
  
      function prepareContentType2() {
        $('table', declarationBlock).wrap('<div class="table-responsive"></div>');
        $('.weiss-form__set_main', declarationBlock).addClass('content-section');
        $('.weiss-form__set_main', declarationBlock).attr('data-empty', 'full');
      }
  
      function prepareContentType1() {
  
        var declaration = $('.declaration-details');
  
        declaration.contents().filter(function() {
          return this.nodeType === 3; // get only the text nodes
        })
        .wrap( "<p></p>" );

        $('header', declaration).each(function(){
          $(this).nextUntil("header").addBack().wrapAll('<div class="nacp-section content-section" />');
        });
  
  
        $('.nacp-section').each(function(index) {
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

      function replaceDeclText4Icons() {
        $('span:contains("[Конфіденційна інформація]")')
          .html(
            '<span class="action-icon">'
              + '<svg xmlns="http://www.w3.org/2000/svg" width="16" viewBox="0 0 576 512" preserveAspectRatio="xMidYMid meet"><path d="M272.702 359.139c-80.483-9.011-136.212-86.886-116.93-167.042l116.93 167.042zM288 392c-102.556 0-192.092-54.701-240-136 21.755-36.917 52.1-68.342 88.344-91.658l-27.541-39.343C67.001 152.234 31.921 188.741 6.646 231.631a47.999 47.999 0 0 0 0 48.739C63.004 376.006 168.14 440 288 440a332.89 332.89 0 0 0 39.648-2.367l-32.021-45.744A284.16 284.16 0 0 1 288 392zm281.354-111.631c-33.232 56.394-83.421 101.742-143.554 129.492l48.116 68.74c3.801 5.429 2.48 12.912-2.949 16.712L450.23 509.83c-5.429 3.801-12.912 2.48-16.712-2.949L102.084 33.399c-3.801-5.429-2.48-12.912 2.949-16.712L125.77 2.17c5.429-3.801 12.912-2.48 16.712 2.949l55.526 79.325C226.612 76.343 256.808 72 288 72c119.86 0 224.996 63.994 281.354 159.631a48.002 48.002 0 0 1 0 48.738zM528 256c-44.157-74.933-123.677-127.27-216.162-135.007C302.042 131.078 296 144.83 296 160c0 30.928 25.072 56 56 56s56-25.072 56-56l-.001-.042c30.632 57.277 16.739 130.26-36.928 171.719l26.695 38.135C452.626 346.551 498.308 306.386 528 256z" fill="#888"/></svg>'
              + '<div class="action-icon__tooltip">'
                + '<div class="action-icon__tooltip-text">Конфіденційна інформація</div>'
              + '</div>'
            + '</span>'
          );
      }
  
    });
  
  })(jQuery);