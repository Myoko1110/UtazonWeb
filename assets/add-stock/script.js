let new_image = [];
$(document).ready(function () {

    const item_id = $(".review-title__item p").data("id");

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

        const item0 = selectedItems.eq(0);

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
            var dataIndex = $(this).data("index");
            indexList.push(dataIndex);
        });
        if (isAllSame){
            $("#item_same").css("display", "block");
            return;
        }

        let hostUrl = location.protocol + '//' + location.host + "/mypage/on_sale/stock/post/";

        let res = confirm("アイテムの在庫を追加しますか？")
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