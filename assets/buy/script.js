$(function(){
    $("#order_confirm").on("click", function (e){
        e.preventDefault();
        items = $(".buy-items").data("items");
        amount = $("#order_confirm").data("amount");

        console.log($("#order_confirm").data("buynow"))
        location.href = "confirm/?items=" + JSON.stringify(items) + "&amount=" + amount + "&buynow=" + $("#order_confirm").data("buynow");
    })
});
