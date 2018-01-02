document.addEventListener(
    "touchstart",
    function(){},
    true
);

function setColumnsHeights (list, item) {
    $list = $(list);
    $items = $list.find(item);
    $items.css('height', 'auto');
    var perRow = Math.round($list.width() / $items.width());

    //let's calc how many cards in row now
    if (perRow == null || perRow < 2) {
        return true;
    }

    for (var i = 0, j = $items.length; i < j; i += perRow) {
        //set all heights in current row to max.height in current row
        var maxHeight = 0,
            $row = $items.slice(i, i + perRow);
        $row.each(function () {
            var itemHeight = parseInt($(this).outerHeight());
            if (itemHeight > maxHeight) maxHeight = itemHeight;
        });
        $row.css('height', maxHeight);
    }
}

$(function() {
    function hideme($ib) {
        $ib.css("height", 10);
    }

    $("#infobox a#closeme").on("click", function() {
        $ib = $('#infobox');

        $ib
            .addClass("animated fadeOutLeftBig")
            .addClass("hideme")
            .one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
                hideme($ib));
    });

    $('#list').on("click", function(event){
        event.preventDefault();
        $('.search-results .item').addClass('list-group-item');
    });

    $('#grid').on("click", function(event){
        event.preventDefault();
        $('.search-results .item')
            .removeClass('list-group-item')
            .addClass('grid-group-item');
    });

    $('.navbar-toggle').on('click', function(){
        $(this).toggleClass('open');
    });

    $('.bi-toggle-search a').on('click', function(e){
        e.preventDefault();
        $('.nav-search').toggleClass('open');
    });

    $('#cta').on('click', function(e){
        e.preventDefault();
        var $activeNav = $('.bi-nav li.active'),
            $next = $activeNav.next('li'),
            $last =  $('.bi-nav li:last-child'),
            $link = $next.find('a');

        $link.trigger('click');
        if ($next.index() === $last.index()) {
            $('#cta').hide();
        }
    });

    $('#bi a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        var anchor = $(this).closest("a"),
            tabPanel = $(anchor.attr("href"));

        if (tabPanel.find("iframe").length == 0) {
            tabPanel.append($("<iframe>").attr("src", anchor.data("iframe-src")));
        }
    });

    //two-way-binding 'dropdown as select' and intput field
    //eg.: <ul class="dropdown-as-select" data-linked-input="someID">
    //     <li><a href="#" data-value="value">value</a></li>
    //..
    //<input id="someID" class="linked-input" value="value" />
    $(".dropdown-as-select li a").click(function(e){
        e.preventDefault();

        var $dropdown = $(this).parents(".dropdown"),
            $dropdownButton = $dropdown.find('.btn'),
            $linkedInput = $('#' + $(this).parents(".dropdown-as-select").data('linked-input'));

        $dropdownButton.html($(this).text() + ' <span class="caret"></span>');
        $dropdownButton.val($(this).data('value'));
        $linkedInput.val($(this).data('value'));
        $linkedInput.change();

        $dropdown.find('li').removeClass('selected');
        $(this).parent('li').addClass('selected');
    });

    function setDropdownsValue() {
        var $linkedInputs = $('.linked-input');

        $linkedInputs.each(function( index ) {
            var $this = $(this),
                id = $this.attr('id'),
                value = $this.val(),
                $dropdownAsSelect = $("[data-linked-input='" + id + "']"),
                $link = $dropdownAsSelect.find("[data-value='" + value + "']");

            if ($link.length > 0) {
                $dropdownAsSelect.find('li').removeClass('selected');
                $link.parent('li').addClass('selected');
                $link.click();
            }
        });
    }//end of two-way-binding 'dropdown as select' and intput field

    function getURLParameters() {
        var url = window.location.href,
            result = [],
            searchIndex = url.indexOf("?");

        if (searchIndex == -1 ) return result;

        var sPageURL = url.substring(searchIndex +1),
            sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++) {
            result[i] = decodeURIComponent(sURLVariables[i].replace(/\+/g, '%20'));
        }
        return result;
    }

    function setExFormStateFromUrl() {
        var urlParams = getURLParameters(),
            usedParams = 0;
        for (var i = 0; i < urlParams.length; i++) {
            var sParameter = urlParams[i].split('='),
                sValue = sParameter[1],
                sName = sParameter[0];

            if(sValue.length > 0) {
                if(sName === 'post_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                    usedParams++;
                }

                if(sName === 'region_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                    usedParams++;
                }

                if(sName === 'region_value') {
                    $('input[name="region_value"]').val(sValue);
                    usedParams++
                }

                if(sName === 'declaration_year')  {
                    $('input[name="declaration_year"]').val(sValue);
                    usedParams++
                }

                if(sName === 'doc_type') {
                    $('input[name="doc_type"]').val(sValue);
                    usedParams++
                }
            }
        }

        if(window.location.hash) {
            var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character

            if(hash === 'exsearch') {
                usedParams++;
            }
        }

        if(usedParams > 0) {
            $('#ex-search-form').addClass('ex-search');
            $('#collapseExSearch').addClass('in');
            $(".ex-search-link").attr("aria-expanded","true");
        }

        $(".ex-search-link").click(function(){
            $(this).hide(400);
        });

        $(document).on('click', '#clear-filters', function(e) {
            e.preventDefault();
            $('input[name="declaration_year"]').val('');
            $('input[name="doc_type"]').val('');
            $('input[name="region_value"]').val('');
            setDropdownsValue();
            $(":checked").attr('checked', false);
        });

        $(document).on('submit', '#ex-form', function(){
            if (!$('input[name="declaration_year"]').val()) {
                $('input[name="declaration_year"]').remove();
            }

            if (!$('input[name="doc_type"]').val()) {
                $('input[name="doc_type"]').remove();
            }

            if (!$('input[name="region_value"]').val()) {
                $('input[name="region_value"]').remove();
            }
        });
    }

    //In case we beed to add other blocks from other pages
    function _setColumnsHeights() {
        setColumnsHeights ('.search-results', '.item');
    }

    //generate table of contest for nacp decls
    function generateTocNacp() {
        $( "<div id='nacp-toc'><a id='toc-collapse' data-toggle='tooltip' data-placement='left' title='Згорнути'><span>Зміст декларації</span></a><h2>Зміст:</h2><ul></ul></div>" ).insertAfter( ".decl-header-wrap .sub-header" );

        //lets find all text without tag = text nodes
        $("#nacp_decl")
            .contents()
            .filter(function() {
                // get only the text nodes
                return this.nodeType === 3;
            })
            .wrap( "<p></p>" );

        $('#nacp_decl header:not(.decl-earnings-header)').each(function(){
            $(this).nextUntil("header").andSelf().wrapAll('<div class="nacp-section" />');
        });

        $('.nacp-section').each(function( index ) {
            var $this = $(this),
                $h2 = $this.find('h2'),
                text = $h2.text(),
                $someInfo = $this.find('table, .personal-info, label');
                emptyClass = '';

            $this.find('header').children().not('h2').insertAfter($this.find('header'));
            $this.children().not('header').wrapAll('<div class="body" />');

            if($someInfo.length == 0) {
                emptyClass = 'empty';
                $this.addClass(emptyClass);
                $this.find('header').attr('data-toggle', 'collapse').attr('data-target', '#collapse-'+index).attr('aria-expanded', 'false');
                $this.find('.body').addClass('collapse').attr('id', 'collapse-'+index).attr('aria-expanded', 'false');
            }

            var a = $('<a />', {
                'href' : '#toc-id-' + index,
                'text' : text,
                'class': emptyClass
            });

            $this.attr('id', 'toc-id-' + index);
            li = $('<li />').append(a).appendTo('#nacp-toc ul');

            // [2.2] - [15]
            if(index > 1 && index < 16) {
                var $body = $this.find('.body');
                $body.each(function(index2) {
                    $(this).find('p').nextUntil('div').andSelf().wrapAll('<div class="help-text collapse" />');
                    var $helpText = $(this).find('.help-text');
                    $helpText.attr('id', 'help-text-collapse-' + index).attr('aria-expanded', 'false');
                    $('<span data-toggle="tooltip" data-placement="top" title="Пояснення щодо цього розділу декларації"><span class="collapse-help-text glyphicon glyphicon-option-horizontal" role="button" data-toggle="collapse" data-target="#help-text-collapse-' + index +'" aria-expanded="false"></span></span>').insertBefore($helpText);
                });
            }
        });

        //add two blocks to TOC
        if( $('#similar_by_surname').length > 0 ) {
            $('<li class="divider"></li>').appendTo('#nacp-toc ul');
            $('<li><a href="#similar_by_surname">Інші декларації за тим же прізвищем</a></li>').appendTo('#nacp-toc ul');
        }

        if( $('#similar_by_relations').length > 0 ) {
            $('<li><a href="#similar_by_relations">Декларації осіб, що можуть бути родичами декларанта</a></li>').appendTo('#nacp-toc ul');
        }

        if($(window).width() < 1600) {
            $( "#toc-collapse" ).css('display', 'inline-block');

            $( "#nacp-toc" ).animate({
                right: -320
            }, 1000, function() {
                $( "#nacp-toc" ).addClass('closed');
                $( "#toc-collapse" ).css('display', 'inline-block').attr('data-original-title', 'Відкрити');
            });
        }

        $(document).on('click', '#nacp-toc ul a', function(){
            event.preventDefault();

            if($(window).width() < 1600) {
                $('#nacp-toc').toggleClass('closed');
            }

            $('html, body').animate({
                scrollTop: $( $.attr(this, 'href') ).offset().top
            }, 500);
        });

        $(document).on('click', '#toc-collapse', function(){
            $('#nacp-toc').toggleClass('closed').css('right', '');

            if ($('#nacp-toc').hasClass('closed')) {
                $('#toc-collapse').attr('data-original-title', 'Відкрити');
            } else {
                $('#toc-collapse').attr('data-original-title', 'Згорнути');
            }
        });
    }

    function replaceDeclText4Icons() {
        $('span:contains("[Конфіденційна інформація]")').html('<div class="decl-hidden-info" data-toggle="tooltip" data-placement="top" title="Конфіденційна інформація"><span class="glyphicon glyphicon-eye-close"></span></div>');
        $('[data-toggle="tooltip"]').tooltip();
    }

    function populateBihusNews(data, $container, ntitle, link) {
        var title = data[0].title,
            nid = data[0].nid,
            teaser_text = data[0].field_teaser_text,
            created = data[0].created,
            big_teaser_media = data[0].field_teaser_media_1.replace(/^\s+|\s+$/g,''),
            declNews = '';

        declNews = declNews + '<div class="top-news"><a target="_blank" class="top-news-card" href="https://bihus.info/node/' + nid +'"><div class="news-block-title">Останні новини ' + ntitle + '</div>';
        declNews = declNews +  '<div class="top-news-container"><img src="' +  big_teaser_media +'" />';
        declNews = declNews +  '<div class="top-news-info"><h4>' + title  + '</h4>';
        declNews = declNews +  '<h6>' + created + '</h6><div class="top-teaser">' + teaser_text + '</div></div>';
        declNews = declNews + '</div></a></div>';

        declNews = declNews + '<div class="more-news"><div class="more-news-container">';

        for(i = 1; i < 6; i ++) {
            title = data[i].title,
                nid = data[i].nid,
                teaser_text = data[i].field_teaser_text,
                created = data[i].created,
                teaser_media = data[i].field_teaser_media;

            declNews = declNews +  '<a target="_blank" class="news-row" title="' + title +'" href="https://bihus.info/node/' + nid +'"><div class="media">';
            declNews= declNews + '<div class="media-left">';
            declNews= declNews + '<div class="media-object"><img src="' + teaser_media +'" />';
            declNews= declNews + '</div></div>';
            declNews= declNews + '<div class="media-body card-body">';
            declNews= declNews + '<div class="card-flip"><div class="face front"><h4 class="media-heading">' + title + '</h4>';
            declNews= declNews + '<h6>' + created + '</h6></div><div class="face back">' + teaser_text +'</div></div>';
            declNews= declNews + '</div></div></a>';
        }

        declNews = declNews + '<a target="_blank" href="' + link + '" class="more-news-more-link">Більше новин тут</a></div></div>';
        $($container).append(declNews);
    }

    function fetchBihusNews() {
        $('body').addClass('ajax-run');

        $.ajax({
                url: 'https://bihus.info/restapi/decl-news',
                type: 'GET'
            })
            .done(function(data) {
                populateBihusNews(data, '#decl-news-block', 'декларацій', 'https://bihus.info/projects/deklaracii');
            })
            .fail(function(event) {
                console.log(event.status);
            });

        $.ajax({
                url: 'https://bihus.info/restapi/bihus-news',
                type: 'GET'
            })
            .done(function(data) {
                populateBihusNews(data, '#decl-bihus-block', 'Bihus.info', 'https://bihus.info/news/all');
            })
            .fail(function(event) {
                console.log(event.status);
            });
    }

    function resizeBi() {
        if($('.bi-analytics-page').length !== 0) {
            var wH = $(window).height(),
                navH = $('.nav-block').height(),
                biNavH = $('.bi-nav').height(),
                $biContainer = $('.bi-frame'),
                newH = wH - navH - biNavH - 40; //40 = cta button outer-height

            if(newH < 600) {
                newH = 600;
            }

            $biContainer.height(newH);
        }
    }

    bootstrapAlert = function () {};
    bootstrapAlert.show = function (message, alert, timeout) {
        $('<div id="floating_alert" class="alert alert-' + alert + ' fade in"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' + message + '&nbsp;&nbsp;</div>').appendTo('body');


        setTimeout(function () {
            $(".alert").alert('close');
        }, timeout);

    };
    
    $(document).ajaxStop(function () {
        $('body').removeClass('ajax-run').addClass('bihus-news-ready');
    });

    $(document).ready(function() {
        if($('.front').length > 0) {
            fetchBihusNews();
        }

        $(".trigger").click(function() {
            $(".chatbot-menu").toggleClass("active");
        });

        $.material.init();
        $('[data-toggle="tooltip"]').tooltip();
        setExFormStateFromUrl();
        setDropdownsValue();

        if($('.declaration-page-nacp').length > 0) {
            generateTocNacp();
            replaceDeclText4Icons();
        }

        resizeBi();

        $(".search-name").typeahead({
            minLength: 2,
            autoSelect: false,
            source: function(query, process) {
                $.get('/ajax/suggest', {"q": query})
                    .success(function(data){
                        process(data);
                    })
            },
            matcher: function() {
                // Big guys are playing here
                return true;
            }
        });

        // submit search form on enter (fix typeahead)
        $('.search-name').on('keydown', function(e) {
            if (e.keyCode == 13) {
                var ta = $(this).data('typeahead'),
                    val = ta.$menu.find('.active').data('value');
                if (val)
                    $(this).val(val);
                $(this.form).submit();
            }
        });
    });

    $( window ).load(function() {
        _setColumnsHeights();
    });

    $(window).resize(function() {
        clearTimeout(window.resizedFinished);

        window.resizedFinished = setTimeout(function(){
            _setColumnsHeights();
            resizeBi();
        }, 250);
    });

});
