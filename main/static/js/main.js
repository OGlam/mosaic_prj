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

var hamburger = {
    navToggle: document.querySelector('.nav-toggle'),
    nav: document.getElementById('user_menu'),

    doToggle: function (e) {
        if (e.target.nodeName === 'A' || e.target.nodeName === 'BUTTON') {
            return;
        }
        e.preventDefault();
        this.navToggle.classList.toggle('expanded');
        this.nav.classList.toggle('expanded');
    }
};

hamburger.navToggle.addEventListener('click', function (e) {
    hamburger.doToggle(e);
});
hamburger.nav.addEventListener('click', function (e) {
    hamburger.doToggle(e);
});
