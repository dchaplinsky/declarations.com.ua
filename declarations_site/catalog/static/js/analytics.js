// Function to generate the dynamic table of contents
jQuery.fn.generate_TOC = function() {
    var base = $(this[0]),
        selectors = ['h1', 'h2', 'h3', 'h4'],
        last_ptr = [{}, {}, {}, {}],
        anchors = {};

    generate_anchor = function(text) {
        var test = text.replace(/\W/g, '_');

        while (test in anchors) {
            //if no suffix, add one
            if (test.match(/_\d+$/) === null) {
                test = test + "_2";
            }
            //else generate unique id for duplicates by adding one to the suffix
            else {
                test = test.replace(/_(\d+)$/, function(match, number) {
                    var num = +number + 1;
                    return ("_" + num)
                });
            }
        }
        anchors[test] = 1;
        return (test);
    }

    $(selectors.join(',')).each(function() {
        var heading = $(this),
            idx = selectors.indexOf(heading.prop('tagName').toLowerCase()),
            itr = 0;

        while (itr <= idx) {
            if (jQuery.isEmptyObject(last_ptr[itr])) {
                last_ptr[itr] = $('<ul>').addClass('nav');
                if (itr === 0) {
                    base.append(last_ptr[itr])
                } else {
                    if (last_ptr[itr - 1].children('li').length === 0) {
                        last_ptr[itr - 1].append(last_ptr[itr]);
                    } else {
                        last_ptr[itr - 1].children('li').last().append(last_ptr[itr]);
                    }
                }
            }
            itr++;
        }
        var anchor = generate_anchor(heading.text());
        heading.attr('id', anchor);
        var a = $('<a>')
            .text(heading.text())
            .attr('href', '#' + anchor);

        var li = $('<li>')
            .append(a);

        last_ptr[idx].append(li);
        for (i = idx + 1; i < last_ptr.length; i++) {
            last_ptr[i] = {};
        }
    });
}

/* run scripts when document is ready */
$(function() {
    "use strict";

    var analytics_wrapper = $('.analytics-wrapper');

    if (analytics_wrapper.length > 0) {
        analytics_wrapper
            .before('<div id="toc" class="well sidebar sidenav hidden-print hidden-xs hidden-sm"/>');
            // .before('<div class="col-md-3"><div id="toc" class="well sidebar sidenav affix hidden-print"/></div>');

        analytics_wrapper.addClass('col-md-offset-3');

        /* table of contents */
        $('#toc').generate_TOC();


        /* size of thumbnails */
        var thumbsize = "col-md-9";

        /* Using render_html, so add in code block */
        analytics_wrapper.find('pre.knitr').each(function() {
            $(this).removeClass('knitr');
            if ($(this).find('code').length < 1) {
                $(this).wrapInner('<code class=' + $(this).attr('class') + '></code>');
            }
        });

        /* style tables */
        analytics_wrapper.find('table').addClass('table table-striped table-bordered table-hover table-condensed');
        analytics_wrapper.find('table').wrap("<div class='table-responsive'></div>");

        /* give images a lightbox and thumbnail classes to allow lightbox and thumbnails TODO: make gallery if graphs are grouped */
        analytics_wrapper.find('div.rimage img').each(function() {

            //remove rimage div
            $(this).unwrap();

            var a = $(this).
            wrap('<a href=# class="media-object pull-left mfp-image thumbnail ' + thumbsize + '"></a>').
            parent();

            var sibs = a.prevUntil('div.rimage,div.media');
            var div = $('<div class="media" />');
            if (sibs.length != 0) {
                sibs.addClass('media-body');
                //need to reverse order as prevUntil puts objects in the order it found them
                $(sibs.get().reverse()).wrapAll(div).parent().prepend(a);
            } else {
                a.wrap(div);
            }
        });

        analytics_wrapper.find('div.chunk').addClass('media');

        /* Magnific Popup */
        analytics_wrapper.find(".thumbnail").each(function() {
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

        $("body").scrollspy({
            target: '#toc',
            offset: 300
        });

        $('#toc').affix({
            offset: {
                top: 300
            }
        });

        //if toc started in affix mode = position fixed
        setTocWidth();

        $('#toc').on('affix.bs.affix', function () {
            setTocWidth();
        });

        $('#toc').on('affix-top.bs.affix', function () {
            $('#toc').css('width', '');
        });

        $( window ).on( 'resize', function () {
            setTocWidth();
        });
    }

    function setTocWidth() {
        var $parentWidth = $('.page-content').width() / 4;
        $('#toc').css('width', $parentWidth + 'px');
    }
});
