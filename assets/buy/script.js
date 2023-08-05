$(function(){
    $("#order_confirm").on("click", function (e){
        e.preventDefault();
        items = $(".buy-items").data("items");

        console.log($("#order_confirm").data("buynow"))
        location.href = "confirm/?items=" + JSON.stringify(items) + "&buynow=" + $("#order_confirm").data("buynow");
    })
});
