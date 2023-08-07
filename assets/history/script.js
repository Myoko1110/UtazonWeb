function order_cancel(element){
    let order_id = element.getAttribute("data-id");
    $("#order_cancel a").attr("href", "../buy/cancel/?id=" + order_id);
    $("#order_cancel").css("display", "flex");
}
