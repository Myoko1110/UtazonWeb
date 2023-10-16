const xhr = new XMLHttpRequest();
$(function () {

    $(".cart-product__number-input").on("input", function () {
        let submit = $(this).parent().find("input[type='button']");
        submit.css("display", "block");
    });

    // カート内のアイテム数を更新
    $(".cart-product__update").on("click", function () {
        const This = $(this)

        let item_id = This.data("id");
        let value = This.parent().find("input[type='number']").val();

        if (value == 0) {
            This.parent().find(".zero-invalid").css("display", "block");
            This.parent().find("input[type='number']").val(1);
            This.css("display", "none");
            value = 1;
        }

        let url = `/cart/update/?id=${item_id}&qty=${value}`;
        $(".buy-load").css("display", "block");

        xhr.open("GET", url, true);
        xhr.send();
        This.css("display", "none");


        xhr.onload = function () {
            let rs = JSON.parse(xhr.response);
            $(".buy-total").each(function () {
                $(this).text(rs.total);
            });
            $(".buy-amount").each(function () {
                $(this).text(rs.amount);
            });
            if (rs.error) {
                if (rs.error["msg"] === "Shortage"){
                    This.parent().find(".shortage").css("display", "block");
                    This.parent().find(".shortage p span").text(rs.error["stock"]);
                    This.parent().find(".cart-product__number-input").val(rs.error["stock"])
                }
                setTimeout(function (){
                    This.parent().find(".shortage").fadeOut(1000);
                }, 4000);
            }

            $(".buy-load").css("display", "none");
        }
    });
});
