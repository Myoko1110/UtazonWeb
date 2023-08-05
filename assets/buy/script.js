$(function(){
    total = $(".buy-confirm__description h3 span").text();
    user_point = Number($(".point").text());

    if ($(".buy-point__input").attr("max") > Number(total) * 10){
        $(".buy-point__input").attr("max", Number(total) * 10);
    }

    total = new Decimal(total);

    $("#order_confirm").on("click", function (e){
        e.preventDefault();

        items = $(".buy-items").data("items");
        point = $(".buy-point__input").val();

        if ($(".buy-point__input").val() > Number(total) * 10){
            $("#error1").css("display", "block");
            return;
        }
        if ($(".buy-point__input").val() > user_point){
            $("#error2").css("display", "block");
            return;
        }
        location.href = "confirm/?items=" + JSON.stringify(items) + "&buynow=" + $("#order_confirm").data("buynow") + "&point=" + point;
    });

    $(".buy-point__input").on("input", function (e){

        point = new Decimal(String($(".buy-point__input").val()));
        frac = new Decimal("0.1");

        PointToPrice = point.mul(frac).toNumber();

        viewPrice = total.sub(PointToPrice).toNumber();
        $(".buy-confirm__description h3 span").text(total.sub(PointToPrice).toNumber());

    })
});
