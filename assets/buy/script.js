$(function(){
    $("#order_confirm").on("click", function (e){
        e.preventDefault();
        items = $(".buy-items").data("items");
        location.href = "confirm/?items=" + JSON.stringify(items);
    })
});
