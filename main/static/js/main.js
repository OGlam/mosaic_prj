$(function () {
    $('#lang-switcher').change(function () {
        $('#lang-form').submit();
    });
    $('.close-user-menu').click(function () {
        $('.user-menu-btn').trigger('click');
    });
    // $("input").each((i, el) => {
    //     if ($(el).attr('id').endsWith("_en")) {
    //         $(el).attr('dir', 'ltr');
    //     }
    //     if ($(el).attr('id').endsWith("_he")) {
    //         $(el).attr('dir', 'rtl');
    //     }
    // });
});
