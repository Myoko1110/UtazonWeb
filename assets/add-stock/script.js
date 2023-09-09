let new_image = [];
$(document).ready(function () {

    const item_id = $(".review-title__item p").data("id");

    // アイテムの選択
    $(".muci-slot div").on("click", function () {
        $(this).toggleClass("isSelectIndex");
    })

    // 送信
    $("#submit").on('click', function () {

        selectedItems = $(".isSelectIndex");

        if ( selectedItems.length === 0) {
            if (selectedElements.length === 0) {
                $("#item_required").css("display", "block");
            }
            return;
        }

        var hostUrl = location.protocol + '//' + location.host + "/mypage/on_sale/stock/post/";

        var indexList = [];
        $(".isSelectIndex").each(function () {
            var dataIndex = $(this).data("index");
            indexList.push(dataIndex);
        });

        params = {
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