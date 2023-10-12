const xhr = new XMLHttpRequest();
$(function () {

    $(".cart-product__number-input").on("input", function () {
        let submit = $(this).parent().find("input[type='button']");
        submit.css("display", "block");
    });

    // カート内のアイテム数を更新
    $(".cart-product__update").on("click", function (){
        let item_id = $(this).data("id");
        let value = $(this).parent().find("input[type='number']").val();

        let url = `/cart/update/?id=${item_id}&qty=${value}`;
        $(".buy-load").css("display", "block");

        xhr.open("GET", url, true);
        xhr.send();
        $(this).css("display", "none");


        xhr.onload = function (){
            let rs = JSON.parse(xhr.response);
            $(".buy-total").each(function (){
                $(this).text(rs.total);
            });
            $(".buy-amount").each(function (){
                $(this).text(rs.amount);
            });
            $(".buy-load").css("display", "none");
        }
    });
});
