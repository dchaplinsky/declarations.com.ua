document.addEventListener(
    "touchstart", 
    function(){},
    true
); 

$(function() { 
    $ib = $('#infobox');
    $.material.init(); 

    function hideme($ib) {
        $ib.css("height", 10);
    }

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
    })
       
    $("#infobox a#closeme").on("click", function() {
        $ib
            .addClass("animated fadeOutLeftBig")
            .addClass("hideme")
            .one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend',
                hideme($ib));
    });

    $.material.init();
   
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
});
