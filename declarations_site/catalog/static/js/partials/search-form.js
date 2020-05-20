(function($) {
  $(function() {
    var searchForm = $('.search-form');

    $(document).on('click', function(e){
      if ( !$(e.target).parents('.search-form__input-wrap').length ) {
        $('.search-form__autocomplete', searchForm).hide();
      }
    });

    /*Open/close Deep Search by click Start*/

    $('.search-form__deep-search', searchForm).on('click', function(e) {
      e.preventDefault();
      $('.deep-search').toggleClass('opened');
    });

    /*Open/close Deep Search by click End*/



    /**/
    searchForm.on('click', '.deep-search__filter-title', function() {
      $(this).parents('.deep-search__filter').toggleClass('opened');
    });

    function setAppliedFiltersCount() {
      var appliedFiltersSelector = '.n-checkbox__input:checked:not(#deepsearch)';
      var filterCount = $(appliedFiltersSelector, searchForm).length;
      $('.deep-search__count-block .filter-count', searchForm).text(filterCount);
      setCountFilterInBtn(filterCount);

      $('.deep-search__filter', searchForm).each(function() {
        var countSelectedFilter = $(appliedFiltersSelector, this).length;
        $('.filter-count', this).remove();
        if(countSelectedFilter) {
          var countBlock = '<div class="filter-count">' + countSelectedFilter + '</div>';
          $('.deep-search__filter-title', this).append(countBlock);
        }
      });
    }

    setAppliedFiltersCount();

    /*Counting selected filters Start*/
    searchForm.on('change', '.n-checkbox__input', setAppliedFiltersCount);

    /*Counting selected filters End*/



    /*Reset filter Start*/

    $('.deep-search__reset', searchForm).on('click', function(e) {
      e.preventDefault();
      $('.n-checkbox__input', searchForm).prop('checked', false);
      $('.deep-search__count-block .filter-count', searchForm).text(0);
      setCountFilterInBtn(0);
      $('.deep-search__filter-title .filter-count', searchForm).remove();
    });

    /*Reset filter End*/



    /*Region Mobile Select Start*/

    $('.region-filter__title', searchForm).on('click', function() {
      if(view === getView()) {
        $('.region-filter__items-wrap', searchForm).toggle();
      }
    });

    $(document).on('click', function(e){
      if ( !$(e.target).parents('.region-filter').length ) {
        $('.region-filter__items-wrap', searchForm).hide();
      }
    });

    /*Region Mobile Select End*/


    /*Rebuild filter Desktop - Mobile Start*/

    var view = getView();
    if(view === 'mobile') {
      rebuildDesktopToMobile();
    }

    window.addEventListener("resize", function () {
      var newView = getView();
      if (newView === 'mobile' && view === 'desktop') {
        rebuildDesktopToMobile();
      }
      if (newView === 'desktop' && view === 'mobile') {
        rebuildMobileToDesktop();
      }
      view = newView;
    });

    function getView() {
      if (window.matchMedia("(min-width: 1024px)").matches) {
        return 'desktop';
      }
      else {
        return 'mobile'
      }
    }

    function rebuildDesktopToMobile() {
      var documentFilter = $('.filter__document-position', searchForm);

      var positionFilter = documentFilter.clone();
      positionFilter.find('.position-filter__document').remove();
      positionFilter.addClass('secondary-position-filter');
      var positionFilterTitle = $('.position-filter__param-title', positionFilter).text();
      $('.mobile', positionFilter).text(positionFilterTitle);
      positionFilter.insertAfter(documentFilter);

      documentFilter.find('.position-filter__position').remove();
      documentFilter.addClass('main-position-filter');
    }

    function rebuildMobileToDesktop() {
      var documentFilter = $('.main-position-filter', searchForm);
      var positionFilter = $('.secondary-position-filter', searchForm);
      $('.position-filter__position', positionFilter).insertAfter($('.position-filter__document', documentFilter));
      positionFilter.remove();
      documentFilter.removeClass('main-position-filter');
    }

    /*Rebuild filter Desktop - Mobile End*/

    function setCountFilterInBtn(filterCount) {
      $('.search-form__deep-search-count', searchForm).text(filterCount || '');
    }

    $('.search-form__input').typeahead({
      minLength: 2,
      autoselect: false,
      hint: false,
      classNames: {
        menu: 'search-form__autocomplete',
        cursor: 'search-form__autocomplete-item--current',
      }
    }, {
      name: 'server',
      source: function(query, _, process) {
        $.get('/search/suggest', {q: query}, function(data) {
          process(data);
        })
      },
      display: function(suggest) {
        return $(suggest).data('sugg_text');
      },
      templates: {
        suggestion: function(item) {
          return $(item);
        }
      }
    }).bind('typeahead:select', function(e, suggestion) {
      var form = $('.search-form__input').closest('form')
      form.submit();
    });
  });

})(jQuery);