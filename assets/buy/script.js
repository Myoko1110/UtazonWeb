$(function(){
    const total = new Decimal($(".buy-confirm__description h3 span").text());
    const user_point = Number($(".point").text());
    const per_point = new Decimal(Number($(".point").data("perpoint")));
    const items = $(".buy-items").data("items");
    const buynow = $("#order_confirm").data("buynow");
    let player_balance = null;
    if ($("#player_balance").data("float")) {
        player_balance = new Decimal($("#player_balance").data("float"));
    }
    if ($(".buy-point__input").attr("max") > total.div(per_point).toNumber()){
        $(".buy-point__input").attr("max", total.div(per_point).toNumber());
    }
    $("#order_confirm").on("click", function (e){
        e.preventDefault();
        console.log(buynow)
        if(buynow === "couldn't access"){
            return;
        }

        let point = Number($(".buy-point__input").val());

        if (point > total.div(per_point).toNumber()){
            $("#error1").css("display", "block");
            $("#error2").css("display", "none");
            $("#error3").css("display", "none");
            return;
        }
        if (point > user_point || point < 0){
            $("#error2").css("display", "block");
            $("#error1").css("display", "none");
            $("#error3").css("display", "none");
            return;
        }
        if (!Number.isInteger(point)){
            $("#error3").css("display", "block");
            $("#error1").css("display", "none");
            $("#error2").css("display", "none");
            return;
        }
        location.href = "confirm/?items=" + JSON.stringify(items) + "&buynow=" + buynow + "&point=" + point;
    });

    $(".buy-point__input").on("input", function (e){

        let InputPoint = new Decimal(String($(".buy-point__input").val()));
        let PointToPrice = InputPoint.mul(per_point);
        let ViewPrice = total.sub(PointToPrice);

        $(".buy-confirm__description h3 span").text(ViewPrice.toNumber().toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
        $("#after_balance").text(player_balance.sub(ViewPrice).toNumber().toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
    });
});
