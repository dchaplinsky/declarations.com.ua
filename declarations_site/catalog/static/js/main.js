document.addEventListener(
    "touchstart",
    function(){},
    true
);

$(function() {
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

    //two-way-binding 'dropdown as select' and intput field
    //eg.: <ul class="dropdown-as-select" data-linked-input="someID">
    //     <li><a href="#" data-value="value">value</a></li>
    //..
    //<input id="someID" class="linked-input" value="value" />
    $(".dropdown-as-select li a").click(function(){
        var $dropdown = $(this).parents(".dropdown"),
            $dropdownButton = $dropdown.find('.btn'),
            $linkedInput = $('#' + $(this).parents(".dropdown-as-select").data('linked-input'));

        $dropdownButton.html($(this).text() + ' <span class="caret"></span>');
        $dropdownButton.val($(this).data('value'));
        $linkedInput.val($(this).data('value'));

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
            result[i] = decodeURIComponent(sURLVariables[i]);
        }
        return result;
    }

    function setExFormStateFromUrl() {
        var urlParams = getURLParameters();
        for (var i = 0; i < urlParams.length; i++) {
            var sParameter = urlParams[i].split('='),
                sValue = sParameter[1],
                sName = sParameter[0];

            if(sValue.length > 0) {
                if(sName === 'post_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                }

                if(sName === 'region_type') {
                    $('input[value="' + sValue + '"]').prop('checked', true);
                }

                if(sName === 'region_value') {
                    $('input[name="region_value"]').val(sValue.replace("+"," "));
                }

                if(sName === 'declaration_year')  {
                    $('input[name="declaration_year"]').val(sValue);
                }

                if(sName === 'doc_type') {
                    $('input[name="doc_type"]').val(sValue.replace("+"," "));
                }
            }
        }

        $(document).on('click', '#clear-filters', function(){
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
        $( "<div id='nacp-toc'><a id='toc-collapse' data-toggle='tooltip' data-placement='left' title='Згорнути'><span>Зміст декларації</span></a><h2>Зміст:</h2><ul></ul></div>" ).insertAfter( ".sub-header" );

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
        if( $('#similar_by_sirname').length > 0 ) {
            $('<li class="devider"></li>').appendTo('#nacp-toc ul');
            $('<li><a href="#similar_by_sirname">Інші декларації за тим же прізвищем</a></li>').appendTo('#nacp-toc ul');
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

    $(document).ready(function() {
        $.material.init();
        $('[data-toggle="tooltip"]').tooltip();
        setExFormStateFromUrl();
        setDropdownsValue();

        if($('.declaration-page-nacp').length > 0) {
            generateTocNacp();
            replaceDeclText4Icons();
        }

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
        $('#search-form').on('keydown', function(e) {
            if (e.keyCode == 13) {
                var ta = $(this).data('typeahead'),
                    val = ta.$menu.find('.active').data('value');
                if (val)
                    $('#search-form').val(val);
                $('#front-searchbox form').submit();
            }
        });
    });

    $( window ).load(function() {
        _setColumnsHeights();
    });

    $( window ).on( 'resize', function () {
        _setColumnsHeights();
    });

});
