//read decl.ID from localstorage and populate compare list
function getCompareList() {
    var c = 0,
        modalBody = $('.decl-compare-modal .modal-body');

    $.each(localStorage, function(key, value){
        if (key.indexOf('declarationID-') >= 0) {
            modalBody.find(".empty-message").hide();
            c++;
            $('.decl-compare-toggle').removeClass('hidden');

            var declarationID = key.substring(14);
            $(value).appendTo(modalBody);
            $(".search-results").find(".decl-item[data-declid='" + declarationID + "']").addClass('selected');

            //we at decl.page and if decl already at list, we must disable button at decl.page
            if($('#page').data('declid') === declarationID) {
                $('.declaration-page #page .add2compare-list').addClass('active').html('У списку порівнянь');
            }
        }
    });

    //update counter at badge
    $('.decl-compare-toggle .badge').html(c);

    //can clear list
    if (c > 0) {
        $('.clear-compare-list').removeClass('hidden');
    }

    //can compare
    if (c > 1) {
        $('.compare-list-action').removeClass('hidden');
    }
}

function ClearCompareList() {
    $.each(localStorage, function(key, value){
        if (key.indexOf('declarationID-') >= 0) {
            var declarationID = key.substring(14);
            localStorage.removeItem("declarationID-" + declarationID);
        }
    });

    //update modal
    $('.decl-compare-modal .modal-body').html('');
    $('.clear-compare-list').addClass('hidden');
    $('.compare-list-action').addClass('hidden');

    //update button
    $('.decl-compare-toggle .badge').html('');
    $('.decl-compare-toggle').addClass('hidden');

    //update decl.page or search results
    $(".search-results .decl-item").removeClass('selected');
    $('.declaration-page #page .add2compare-list').removeClass('active').html('<i class="fa fa-balance-scale" aria-hidden="true"></i> Додати декларацію у список порівнянь');
}

//add declaration 2 compare list by click
$(document).on('click', '.search-results .add2compare-list', function(e){
    e.preventDefault();

    var $this = $(e.target),
        $parentBox = $this.parents('.decl-item'),
        $compareContainer = $('.decl-compare-modal .modal-body'),
        $cloneItem = $parentBox.clone(),
        declarationID = $parentBox.data('declid');

    $cloneItem.append('<input type="hidden" name="declaration_id" value="' + declarationID + '" />');

    //add only if not in list already
    if (localStorage.getItem("declarationID-" + declarationID) === null) {
        localStorage.setItem("declarationID-" + declarationID, $cloneItem.addClass('selected').prop('outerHTML'));
        $cloneItem.addClass('selected').appendTo($compareContainer);
        $compareContainer.find(".empty-message").hide();
        $this.parents('.decl-item').addClass('selected');

        //show message to user
        bootstrap_alert.warning('Декларацію додано до списку порівнянь', 'success', 2000);

        var c = 0;
        $.each(localStorage, function(key, value){
            if (key.indexOf('declarationID-') >= 0) {
                c++;
            }
        });

        //add counter to badge
        $('.decl-compare-toggle .badge').html(c);

        //if user just add first decl. let's show him the button
        if (c === 1) {
            $("html, body").animate({ scrollTop: 0 }, "slow");
            $('.decl-compare-toggle').removeClass('hidden').addClass('pulse');
        }

        //can clear
        if (c > 0) {
            $('.clear-compare-list').removeClass('hidden');
        }

        //can compare
        if (c > 1) {
            console.log('1');
            $('.compare-list-action').removeClass('hidden');
        }
    }
});

//remove declaration from compare-list
$(document).on('click', '.decl-compare-modal .modal-body .add2compare-list', function(e){
    e.preventDefault();

    var $this = $(e.target),
        $parentBox = $this.parents('.decl-item'),
        declarationID = $parentBox.data('declid');

    $parentBox.remove();

    //remove from local storage
    localStorage.removeItem("declarationID-" + declarationID);

    var c = 0;
    $.each(localStorage, function(key, value){
        if (key.indexOf('declarationID-') >= 0) {
            c++;
        }
    });

    //add counter to badge
    $('.decl-compare-toggle .badge').html(c);

    //update modal and button
    if( c < 1) {
        $('.decl-compare-toggle .badge').html('');
        $('.decl-compare-toggle').addClass('hidden');
        $('.decl-compare-modal').modal('hide');
        $('.compare-list-action').addClass('hidden');
        $('.clear-compare-list').addClass('hidden');
    }

    //can't compare
    if (c < 2) {
        $('.compare-list-action').addClass('hidden');
    }

    //restore add2compare button at search results
    $(".search-results").find(".decl-item[data-declid='" + declarationID + "']").removeClass('selected');

    //restore add2compare button at decl.page
    if($('#page').data('declid') === declarationID) {
        $('.declaration-page #page .add2compare-list').removeClass('active').html('<i class="fa fa-balance-scale" aria-hidden="true"></i> Додати декларацію у список порівнянь');
    }
});

//add declaration 2 compare list by click from declaration-page
$(document).on('click', '.declaration-page #page .add2compare-list', function(e){
    var $container = $('.declaration-page #page'),
        name = $container.find('#page-header span').text(),
        desc = $container.find('.sub-header').prop('outerHTML'),
        declarationID = $('#page').data('declid'),
        url = '/declaration/' + declarationID,
        itemHtml = '<div class="decl-item item col-sm-12  col-md-6 col-lg-4 grid-group-item nacp selected" itemscope="" itemtype="http://schema.org/Person"  data-declid="';

    itemHtml = itemHtml + declarationID + '"><div class="box"><a href="#" class="add2compare-list" title="Додати у список порівнянь"><i class="fa fa-times" aria-hidden="true"></i>';
    itemHtml = itemHtml + '<i class="fa fa-plus" aria-hidden="true"></i><i class="fa fa-balance-scale" aria-hidden="true"></i></a><h3><a href="/declaration/'+ declarationID + '" itemprop="name">';
    itemHtml = itemHtml +  name + '</a></h3>';
    itemHtml = itemHtml + desc + '</div></div>';
    itemHtml = itemHtml + '<input type="hidden" name="declaration_id" value="' + declarationID + '" />';

    if (localStorage.getItem("declarationID-" + declarationID) === null) {
        localStorage.setItem("declarationID-" + declarationID, itemHtml);

        $('.declaration-page #page .add2compare-list').addClass('active').html('У списку порівнянь');
        $('.decl-compare-modal .modal-body').html($('.decl-compare-modal .modal-body').html() + itemHtml);

        //show message to user
        bootstrap_alert.warning('Декларацію додано до списку порівнянь', 'success', 2000);

        var c = 0;
        $.each(localStorage, function(key, value){
            if (key.indexOf('declarationID-') >= 0) {
                c++;
            }
        });

        //add counter to badge
        $('.decl-compare-toggle .badge').html(c);

        //if user just add first decl. let's show him the button
        if (c === 1) {
            $("html, body").animate({ scrollTop: 0 }, "slow");
            $('.decl-compare-toggle').removeClass('hidden').addClass('pulse');
        }

        //can clear
        if (c > 0) {
            $('.clear-compare-list').removeClass('hidden');
        }

        //can compare
        if (c > 1) {
            $('.compare-list-action').removeClass('hidden');
        }
    }

});

$(document).on('click', '.clear-compare-list', function(e){
    e.preventDefault();
    ClearCompareList();
});


$(function() {
    getCompareList();
});

$('.decl-compare-modal').on('shown.bs.modal', function () {
    setColumnsHeights ('.decl-compare-modal .modal-body', '.item');
});

$( window ).on( 'resize', function () {
    setColumnsHeights ('.decl-compare-modal.in .modal-body', '.item');
});
