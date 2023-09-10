const xhr = new XMLHttpRequest();

$(function () {

    // カート内のアイテム数を更新
    $(".cart-product__number-input").on("input", function () {
        let item_id = $(this).data("id");
        let value = $(this).val();

        let url = `http://${location.host}/cart/update/?id=${item_id}&n=${value}`;

        xhr.open("GET", url, true);
        xhr.send();
    });
});
