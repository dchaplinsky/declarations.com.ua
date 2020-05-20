(function($) {
    function close() {
        $('.popup').hide();
    }

    $(function() {
        close();

        $(document)
            .on('click', '.modal__trigger', function(e) {
                e.preventDefault();
                $('#' + $(this).data('modalId')).show();
            })
            .on('click', '.popup__close', close)
            .on('keydown', function(e) {
                // ESC
                if (e.which === 27) {
                    close();
                }
            });
    });
})(jQuery);
