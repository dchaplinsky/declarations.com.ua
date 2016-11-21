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
        $('#search-results .item').addClass('list-group-item');
    });

    $('#grid').on("click", function(event){
        event.preventDefault();
        $('#search-results .item')
            .removeClass('list-group-item')
            .addClass('grid-group-item');
    });

    $('.navbar-toggle').on('click', function(){
        $(this).toggleClass('open');
    });

    //In case we beed to add other blocks from other pages
    function _setColumnsHeights() {
        setColumnsHeights ('#search-results', '.item');
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

    });

    $( window ).load(function() {
        _setColumnsHeights();
    });

    $( window ).on( 'resize', function () {
        _setColumnsHeights();
    });

});
