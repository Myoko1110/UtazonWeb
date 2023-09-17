let selected = "all";
$(function () {
    let logo = $(".nav-belt__logo").outerWidth(true);
    let menu = $(".nav-belt__menu").outerWidth(true);
    let address = $(".nav-belt__address").outerWidth(true);
    let account = $(".nav-belt__account").outerWidth(true);
    let returns = $(".nav-belt__returns").outerWidth(true);
    let cart = $(".nav-belt__cart").outerWidth(true);
    let window_width = $(window).width();

    let suggestData;
    $.ajax({
        url: '/suggest/',
        type: 'GET',
        dataType: "json",
    }).done(function (data) {
        const data_stringify = JSON.stringify(data);
        suggestData = JSON.parse(data_stringify);

    }).fail(function (data) {
        // error
        console.log('error');
    });

    if (window_width >= 1000) {
        width = window_width - (logo + address + account + returns + cart) - 165;
    } else if (window_width >= 800) {
        width = window_width - (logo + account + cart) - 165;
    } else {
        width = window_width - 75;
    }
    $(".nav-belt__search-input").css("width", width);

    const host = window.location.host;
    $("#search").submit(function (e) {
        e.preventDefault();
        let query = $("#search_query").val();

        if (selected === "all") {
            location.href = `//${host}/search/?q=${query}`;
        } else {
            location.href = `//${host}/search/?q=${query}&category=${selected}`;
        }
    });

    window.addEventListener('resize', function () {
        logo = $(".nav-belt__logo").outerWidth(true);
        menu = $(".nav-belt__menu").outerWidth(true);
        address = $(".nav-belt__address").outerWidth(true);
        account = $(".nav-belt__account").outerWidth(true);
        returns = $(".nav-belt__returns").outerWidth(true);
        cart = $(".nav-belt__cart").outerWidth(true);
        window_width = $(window).width();

        if (window_width >= 1000) {
            width = window_width - (logo + address + account + returns + cart) - 165;
        } else if (window_width >= 800) {
            width = window_width - (logo + account + cart) - 165;
        } else {
            width = window_width - 75;

        }
        $(".nav-belt__search-input").css("width", width);
    });

    $(".nav-belt__search-select").on("change", function () {
        selected = $("option:selected").val();
    });

    $(".nav-belt__menu").click(function () {
        $(this).toggleClass('active');
        $(".nav-mobile").toggleClass('isActive');
        $(".nav-mobile__background").toggleClass('isActive');
        $(".wrapper").toggleClass('isActive');
    });

    $(".nav-belt__search-input").on("click", function () {
        $(".nav-belt__search-background").fadeIn(100);
    });
    $(".nav-belt__search-background").on("click", function () {
        $(".nav-belt__search-background").fadeOut(100);
    });
    $(".nav-belt__search-input").autocomplete({
        source: function (request, response) {
            var suggests = [];
            var regexp = new RegExp('(' + request.term + ')');

            $.each(suggestData, function (i, values) {
                for (let i = 0; i < values.length; i++) {
                    if (values[i].match(regexp)) {
                        suggests.push(values[0]);
                        return true;
                    }
                }
            });

            response(suggests);
        },
        autoFocus: false,
        delay: 200,
        minLength: 1,
        select: function (event, ui) {
            let selectedValue = ui.item.value;
            location.href = "/search/?q=" + selectedValue;
        },
        close: function (event, ui) {
            $(".nav-belt__search-background").css("display", "none");
        }
    });
});

function close_box() {
    $("#expires").css("display", "none");
    $("#logout").css("display", "none");
    $("#order_cancel").css("display", "none");
    $("#delete").css("display", "none");
    $("#order_redelivery").css("display", "none");
}

function sleep(waitMsec) {
    var startMsec = new Date();

    // 指定ミリ秒間だけループさせる（CPUは常にビジー状態）
    while (new Date() - startMsec < waitMsec) ;
}

function logout_confirm() {
    $("#logout").css("display", "flex");
}