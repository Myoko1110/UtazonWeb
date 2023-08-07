$(function() {
    logo = $(".nav-belt__logo").outerWidth(true);
    address = $(".nav-belt__address").outerWidth(true);
    account = $(".nav-belt__account").outerWidth(true);
    returns = $(".nav-belt__returns").outerWidth(true);
    cart = $(".nav-belt__cart").outerWidth(true);
    window_width = $(window).width();

    if (window_width > 999){
        width = window_width - (logo + address + account + returns + cart) - 165;
    }else{
        width = window_width - (logo + account + cart) - 165;
    }
    $(".nav-belt__search-input").css("width", width);

    const host = window.location.host;
    $("#search").submit(function (e){
        e.preventDefault();
        let query = $("#search_query").val();
        location.href = `//${host}/search/?q=${query}`;
    });

    window.addEventListener('resize', function() {
        logo = $(".nav-belt__logo").outerWidth(true);
        address = $(".nav-belt__address").outerWidth(true);
        account = $(".nav-belt__account").outerWidth(true);
        returns = $(".nav-belt__returns").outerWidth(true);
        cart = $(".nav-belt__cart").outerWidth(true);
        window_width = $(window).width();

        if (window_width > 999){
            width = window_width - (logo + address + account + returns + cart) - 165;
        }else{
            width = window_width - (logo + account + cart) - 165;
        }
        $(".nav-belt__search-input").css("width", width);
    });
});

function close_box(){
    $("#expires").css("display", "none");
    $("#logout").css("display", "none");
    $("#order_cancel").css("display", "none");
}

function logout_confirm(){
    $("#logout").css("display", "flex");
}