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

    $('#login-modal').on('shown.bs.modal', function (e) {
        var href = $(e.relatedTarget).data('href');
        if (href) {
            href = href.replace('?', '%3F').replace('&', '%26');
            $(e.currentTarget).find('#signin a').each(function (){
                this.href = this.href.replace('?next=', '?next='+href+'&origin=');
            });
        }
    });

    function _showLoginModal() {
        var href = window.location.href,
            pos = href.search('login_to=');
        if (pos > 0)
            href = href.substr(pos+9);
        $('#login-modal #signin a').each(function (){
            this.href = this.href.replace('?next=', '?next='+href+'&origin=');
        });
        $('#login-modal').modal('show');
    }

    //In case we beed to add other blocks from other pages
    function _setColumnsHeights() {
        setColumnsHeights ('.search-results', '.item');
    }

    $(document).ready(function() {
        $.material.init();

        $("#search-form").typeahead({
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

        if (window.location.href.search('login_to=') > 0) {
            setTimeout(_showLoginModal, 500);
        }
    });

    $( window ).load(function() {
        _setColumnsHeights();
    });

    $( window ).on( 'resize', function () {
        _setColumnsHeights();
    });

});
