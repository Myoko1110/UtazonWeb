let new_image = [];
$(document).ready(function () {
    $("#item_required").css("display", "none");
    $("#item_over").css("display", "none");
    $("#item_same").css("display", "none");

    const item_id = $(".review-title__item p").data("id");
    const stock = $(".review-title__item").data("stock");

    // アイテムの選択
    $(".muci-slot div").on("click", function () {
        $(this).toggleClass("isSelectIndex");
    })

    // 送信
    $("#submit").on('click', function () {

        let selectedItems = $(".isSelectIndex");

        if (selectedItems.length === 0) {
            $("#item_required").css("display", "block");
            return;
        }

        if (Number(stock) + selectedItems.length > 5000) {
            $("#item_over").css("display", "block");
            return;
        }

        const item0 = $(".review-title__item");

        let isAllSame = false;
        let indexList = [];
        selectedItems.each(function() {
            if ($(this).data("namespacedkey") !== item0.data("namespacedkey")){
                isAllSame = true;
            }
            if ($(this).data("amount") !== item0.data("amount")){
                isAllSame = true;
            }
            if (JSON.stringify($(this).data("enchantment")) !== JSON.stringify(item0.data("enchantment"))){
                isAllSame = true;
            }
            if ($(this).data("damage") !== item0.data("damage")){
                isAllSame = true;
            }
            if ($(this).data("name") !== item0.data("name")){
                isAllSame = true;
            }
            var dataIndex = $(this).data("index");
            indexList.push(dataIndex);
        });
        if (isAllSame){
            $("#item_same").css("display", "block");
            return;
        }

        let hostUrl = location.protocol + '//' + location.host + "/mypage/available/stock/post/";

        let res = confirm("商品の在庫を追加しますか？")
        if (!res){
            return;
        }

        let params = {
            items: JSON.stringify(indexList),
            item_id: item_id
        };

        post(hostUrl, params);

    });
});


function post(path, params, method = 'post') {
    const form = document.createElement('form');
    form.method = method;
    form.action = path;

    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}