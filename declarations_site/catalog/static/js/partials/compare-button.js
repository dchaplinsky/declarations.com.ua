// (function($) {
//     var keyPrefix = 'declarationID-';

//     //helper function to update some strings and values for decl.compare feature
//     function updateCompareStrings(declsInLocalStorage) {
//         // -1: let's count items in local storage
//         // >=0 : we already counted and pass value here
//         if (declsInLocalStorage < 0) {
//             var c = 0;

//             $.each(localStorage, function(key, value){
//                 if (key.indexOf(keyPrefix ) >= 0) {
//                     c++;
//                 }
//             });
//         } else {
//             c = declsInLocalStorage;
//         }

//         //update counter at badge
//         $('.action-icon__count-compared, .count-block__count').html(c);

//         //can clear list
//         // if (c > 0) {
//         //     $('.clear-compare-list').removeClass('hidden');
//         //     $('.decl-compare-modal .modal-body h2').text('');
//         // }

//         //if user just add first decl. let's show him the button
//         if (c === 1) {
//             $("html, body").animate({ scrollTop: 0 }, "slow");
//             $('.header__compare').addClass('pulse');
//         }

//         // //can compare
//         // if (c > 1) {
//         //     $('.compare-list-action').removeClass('hidden');
//         // }

//         //update modal and button
//         if( c < 1) {
//             $('.action-icon__count-compared, .count-block__count').html('');
//             $('.header__compare').addClass('hidden');
//             // $('.decl-compare-modal').modal('hide');
//             // $('.compare-list-action').addClass('hidden');
//             // $('.clear-compare-list').addClass('hidden');
//             // $('.decl-compare-modal .modal-body h2').text('Це сторінка порівняння декларацій. Ви не додали жодної декларації і нам нема чого порівнювати. Зробіть це. Зробіть швидше.');
//         }

//         //can't compare
//         if (c < 2) {
//             $('.compare-list-action').addClass('hidden');
//         }
//     }

//     function getCompareList() {
//         var c = 0;
    
//         $.each(localStorage, function(key, value){
//             if (key.indexOf(keyPrefix) >= 0) {
//                 c++;
//                 $('.decl-compare-toggle').removeClass('hidden');
    
//                 var declarationID = key.substring(keyPrefix.length);
//                 $(value).appendTo($('#compare__popup .compare-popup__items'));
//                 $(".search-card[data-declid='" + declarationID + "']").addClass('search-card--selected');
    
//                 // //we at decl.page and if decl already at list, we must disable button at decl.page
//                 // if ($('#page').data('declid') === declarationID) {
//                 //     $('.declaration-page #page .on-page-button.add2compare-list').addClass('active').html('У списку порівнянь');
//                 // }
//             }
//         });
    
//         updateCompareStrings(c);
//     }    

//     $(function() {
//         getCompareList();
//     });

//     //add declaration 2 compare list by click
//     $(document)
//         .on('click', '.card-actions__action-add-to-compare', function(e) {
//             e.preventDefault();

//             var $this = $(e.target),
//                 $parentBox = $this.parents('.search-card'),
//                 $compareContainer = $('.compare-popup .compare-popup__items'),
//                 $cloneItem = $parentBox.clone(),
//                 declarationID = $parentBox.data('declid');

//             //add only if not in list already
//             if (localStorage.getItem(keyPrefix + declarationID) === null) {
//                 localStorage.setItem(keyPrefix + declarationID, $cloneItem.addClass('search-card--collapsed selected').prop('outerHTML'));
//                 $cloneItem.addClass('search-card--collapsed selected').appendTo($compareContainer);

//                 updateCompareStrings(-1);
//             }
//         })
//         .on('click', '.card-actions__action--close', function() {
//             var $this = $(this),
//                 card = $this.closest('.search-card');
//             localStorage.removeItem('declarationID-' + card.data('declid'));
//             card.remove();
            
//             updateCompareStrings(-1);
//         })
//         .on('click', '.card-actions__action--expand', function() {
//             let $this = $(this);
//             $this.toggleClass('drop-down-btn_opened');
//             $this.closest('.search-card').toggleClass('search-card--collapsed');
//           });

// })(jQuery);
