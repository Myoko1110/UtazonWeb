let selected = "all";
$(function() {
    logo = $(".nav-belt__logo").outerWidth(true);
    menu = $(".nav-belt__menu").outerWidth(true);
    address = $(".nav-belt__address").outerWidth(true);
    account = $(".nav-belt__account").outerWidth(true);
    returns = $(".nav-belt__returns").outerWidth(true);
    cart = $(".nav-belt__cart").outerWidth(true);
    window_width = $(window).width();

    if (window_width >= 1000){
        width = window_width - (logo + address + account + returns + cart) - 165;
    }else if(window_width >= 800){
        width = window_width - (logo + account + cart) - 165;
    }else{
        width = window_width - menu - 75;
    }
    $(".nav-belt__search-input").css("width", width);

    const host = window.location.host;
    $("#search").submit(function (e){
        e.preventDefault();
        let query = $("#search_query").val();

        if (selected === "all"){
            location.href = `//${host}/search/?q=${query}`;
        }else{
            location.href = `//${host}/search/?q=${query}&category=${selected}`;
        }
    });

    window.addEventListener('resize', function() {
        logo = $(".nav-belt__logo").outerWidth(true);
        menu = $(".nav-belt__menu").outerWidth(true);
        address = $(".nav-belt__address").outerWidth(true);
        account = $(".nav-belt__account").outerWidth(true);
        returns = $(".nav-belt__returns").outerWidth(true);
        cart = $(".nav-belt__cart").outerWidth(true);
        window_width = $(window).width();

        if (window_width >= 1000){
            width = window_width - (logo + address + account + returns + cart) - 165;
        }else if(window_width >= 800){
            width = window_width - (logo + account + cart) - 165;
        }else{
            width = window_width - menu - 75;

        }
        $(".nav-belt__search-input").css("width", width);
    });

    $(".nav-belt__search-select").on("change", function (){
        selected = $("option:selected").val();
    });

    $(".nav-belt__menu").click(function () {
        $(this).toggleClass('active');
        $(".nav-mobile").toggleClass('isActive');
        $(".nav-mobile__background").toggleClass('isActive');
        $(".wrapper").toggleClass('isActive');
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