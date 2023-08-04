$(function(){
    $("#order_confirm").on("click", function (e){
        e.preventDefault();
        items = $(".buy-items").data("items");

        if($(".order_confirm").data("buynow") === "True"){
            location.href = "confirm/?items=" + JSON.stringify(items) + "&buy_now=True";
        }else{
            location.href = "confirm/?items=" + JSON.stringify(items);
        }
    })
});
