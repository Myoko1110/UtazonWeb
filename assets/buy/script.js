let express = false;

let point_span;
let submit_button;
let point_input;
let amount_view;

let total;
let user_point;
let per_point;
let point_return;
let items;
let buynow;
let express_price;
let pride_status;

$(function () {
    point_span = $(".point");
    submit_button = $("#order_confirm");
    point_input = $(".buy-point__input");
    amount_view = $(".buy-confirm__description h3 span");

    total = new Decimal(amount_view.data("total"));
    user_point = Number(point_span.text());
    per_point = new Decimal(point_span.data("perpoint"));
    point_return = new Decimal(point_span.data("return")).div(new Decimal("100"));
    items = $(".buy-items").data("items");
    buynow = submit_button.data("buynow");
    express_price = new Decimal($(".buy-way__radio").data("express"));
    pride_status = $(".buy-title").data("prime");

    // ユーザーの残高を取得
    let player_balance = null;
    if ($("#player_balance").data("float")) {
        player_balance = new Decimal($("#player_balance").data("float"));
    }

    // max設定
    if (point_input.attr("max") > total.div(per_point).toNumber()) {
        point_input.attr("max", total.div(per_point).toNumber());
    }

    // 購入確定ボタンを押したときの処理
    submit_button.on("click", function (e) {
        e.preventDefault();
        if (buynow === "fail to connect") {
            return;
        }

        let point = Number($(".buy-point__input").val());

        if (point > total.div(per_point).toNumber()) {
            $("#error1").css("display", "block");
            $("#error2").css("display", "none");
            $("#error3").css("display", "none");
            return;
        }
        if (point > user_point || point < 0) {
            $("#error2").css("display", "block");
            $("#error1").css("display", "none");
            $("#error3").css("display", "none");
            return;
        }
        if (!Number.isInteger(point)) {
            $("#error3").css("display", "block");
            $("#error1").css("display", "none");
            $("#error2").css("display", "none");
            return;
        }

        shippingMethod = $(".buy-way__radio-input:checked").val();

        // location.href = "confirm/?items=" + items + "&buynow=" + buynow + "&point=" + point + "&shipping=" + shippingMethod;
        const params = {
            items: items,
            buynow: buynow,
            point: point,
            shipping: shippingMethod,
        }
        post("/buy/confirm/", params)
    });

    // ポイント設定したときの処理
    point_input.on("input", update_price);

    $(".buy-way__radio-input").on("click", function (e) {
        if ($(this).val() === "prime") {
            if (pride_status !== "True"){
                $("#pride").css("display", "flex");
                e.preventDefault();
            }
        }
        express = $(this).val() === "express";
        update_price()
    });

    $(".box__pride-btn1").on("click", function (){
        $("#pride").css("display", "none");
    });
    $("#pride_close").on("click", function (){
        $("#pride").css("display", "none");
    });
});

function update_price() {
    // 入力されたポイント
    let InputPoint = new Decimal(String($(".buy-point__input").val()));

    // ポイントを金額に変換
    let PointToPrice = InputPoint.mul(per_point);

    // 請求額からポイントを減算
    let ViewPrice = total.sub(PointToPrice);

    try {
        let player_balance_after = player_balance.sub(ViewPrice);
        $("#after_balance").text(player_balance_after.toNumber().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));
    } catch (TypeError) {}

    let point = ViewPrice.mul(point_return)

    $("#get_point").text(point.toNumber().toLocaleString(undefined, {maximumFractionDigits: 2}));


    if (!express) {
        amount_view.text(ViewPrice.toNumber().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));
    } else {
        amount_view.text(ViewPrice.add(express_price).toNumber().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));
    }
}

function post(path, params, method = 'post') {
    const form = document.getElementById("post_form");
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
