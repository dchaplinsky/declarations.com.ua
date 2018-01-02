var keyPrefix = 'declarationID-';

//helper function to update some strings and values for decl.compare feature
function updateCompareStrings(declsInLocalStorage) {
    // -1: let's count items in local storage
    // >=0 : we already counted and pass value here

    if (declsInLocalStorage < 0) {
        var c = 0;

        $.each(localStorage, function(key, value){
            if (key.indexOf(keyPrefix ) >= 0) {
                c++;
            }
        });
    } else {
        c = declsInLocalStorage;
    }

    //update counter at badge
    $('.decl-compare-toggle .badge').html(c);

    //can clear list
    if (c > 0) {
        $('.clear-compare-list').removeClass('hidden');
        $('.decl-compare-modal .modal-body h2').text('');
    }

    //if user just add first decl. let's show him the button
    if (c === 1) {
        $("html, body").animate({ scrollTop: 0 }, "slow");
        $('.decl-compare-toggle').removeClass('hidden').addClass('pulse');
    }

    //can compare
    if (c > 1) {
        $('.compare-list-action').removeClass('hidden');
    }

    //update modal and button
    if( c < 1) {
        $('.decl-compare-toggle .badge').html('');
        $('.decl-compare-toggle').addClass('hidden');
        $('.decl-compare-modal').modal('hide');
        $('.compare-list-action').addClass('hidden');
        $('.clear-compare-list').addClass('hidden');
        $('.decl-compare-modal .modal-body h2').text('Це сторінка порівняння декларацій. Ви не додали жодної декларації і нам нема чого порівнювати. Зробіть це. Зробіть швидше.');
    }

    //can't compare
    if (c < 2) {
        $('.compare-list-action').addClass('hidden');
    }
}

//read decl.ID from localstorage and populate compare list
function getCompareList() {
    var c = 0;

    $.each(localStorage, function(key, value){
        if (key.indexOf(keyPrefix) >= 0) {
            c++;
            $('.decl-compare-toggle').removeClass('hidden');

            var declarationID = key.substring(keyPrefix.length);
            $(value).appendTo($('.decl-compare-modal .modal-body .compare-container'));
            $(".search-results").find(".decl-item[data-declid='" + declarationID + "']").addClass('selected');

            //we at decl.page and if decl already at list, we must disable button at decl.page
            if ($('#page').data('declid') === declarationID) {
                $('.declaration-page #page .on-page-button.add2compare-list').addClass('active').html('У списку порівнянь');
            }
        }
    });

    updateCompareStrings(c);
}

function ClearCompareList() {

    $.each(localStorage, function(key, value){
        if (key.indexOf(keyPrefix) >= 0) {
            var declarationID = key.substring(keyPrefix.length);
            localStorage.removeItem(keyPrefix + declarationID);
        }
    });

    //update modal
    $('.decl-compare-modal .modal-body .compare-container').html('');
    $('.decl-compare-modal .modal-body h2').text('Це сторінка порівняння декларацій. Ви не додали жодної декларації і нам нема чого порівнювати. Зробіть це. Зробіть швидше.');
    $('.clear-compare-list').addClass('hidden');
    $('.compare-list-action').addClass('hidden');

    //update button
    $('.decl-compare-toggle .badge').html('');
    $('.decl-compare-toggle').addClass('hidden');

    //update decl.page or search results
    $(".search-results .decl-item").removeClass('selected');
    $('.declaration-page #page .on-page-button.add2compare-list').removeClass('active').html('<i class="fa fa-balance-scale" aria-hidden="true"></i> Додати декларацію у список порівнянь');
}

//add declaration 2 compare list by click
$(document).on('click', '.search-results .add2compare-list', function(e){
    e.preventDefault();

    var $this = $(e.target),
        $parentBox = $this.parents('.decl-item'),
        $compareContainer = $('.decl-compare-modal .modal-body .compare-container'),
        $cloneItem = $parentBox.clone(),
        declarationID = $parentBox.data('declid');

    //add only if not in list already
    if (localStorage.getItem(keyPrefix + declarationID) === null) {
        localStorage.setItem(keyPrefix + declarationID, $cloneItem.addClass('selected').prop('outerHTML'));
        $cloneItem.addClass('selected').appendTo($compareContainer);
        $this.parents('.decl-item').addClass('selected');

        //show message to user
        bootstrapAlert.show('Декларацію додано до списку порівнянь', 'success', 2000);

        updateCompareStrings(-1);
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
    localStorage.removeItem(keyPrefix + declarationID);

    updateCompareStrings(-1);

    //restore add2compare button at search results
    $(".search-results").find(".decl-item[data-declid='" + declarationID + "']").removeClass('selected');

    //restore add2compare button at decl.page
    if($('#page').data('declid') === declarationID) {
        $('.declaration-page #page .on-page-button.add2compare-list').removeClass('active').html('<i class="fa fa-balance-scale" aria-hidden="true"></i> Додати декларацію у список порівнянь');
    }

    setColumnsHeights ('.decl-compare-modal .modal-body .compare-container', '.item');
});

//add declaration 2 compare list by click from declaration-page
$(document).on('click', '.declaration-page #page .add2compare-list', function(e){
    var declarationID = $('#page').data('declid'),
        itemHtml = $('.decl-teaser').html();

    if (localStorage.getItem(keyPrefix + declarationID) === null) {
        localStorage.setItem(keyPrefix + declarationID, itemHtml);

        $('.declaration-page #page .on-page-button.add2compare-list').addClass('active').html('У списку порівнянь');
        $('.decl-compare-modal .modal-body .compare-container').html($('.decl-compare-modal .modal-body .compare-container').html() + itemHtml);

        //show message to user
        bootstrapAlert.show('Декларацію додано до списку порівнянь', 'success', 2000);

        updateCompareStrings(-1);
    }
});

$(document).on('click', '.clear-compare-list', function(e){
    e.preventDefault();
    ClearCompareList();
});

$(document).ready(function() {
    getCompareList();
});

$('.decl-compare-modal').on('shown.bs.modal', function () {
    setColumnsHeights ('.decl-compare-modal .modal-body .compare-container', '.item');
});

$( window ).on( 'resize', function () {
    setColumnsHeights ('.decl-compare-modal.in .modal-body .compare-container', '.item');
});
