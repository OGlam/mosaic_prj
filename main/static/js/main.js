$(function () {
    $('#lang-switcher').change(function () {
        $('#lang-form').submit();
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
