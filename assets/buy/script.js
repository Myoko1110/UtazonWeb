$(function () {
    const point_span = $(".point");
    const submit_button = $("#order_confirm");
    const point_input = $(".buy-point__input");
    const amount_view = $(".buy-confirm__description h3 span");

    const total = new Decimal(amount_view.data("total"));
    const user_point = Number(point_span.text());
    const per_point = new Decimal(point_span.data("perpoint"));
    const point_return = new Decimal(point_span.data("return"));
    const items = $(".buy-items").data("items");
    const buynow = submit_button.data("buynow");

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
        location.href = "confirm/?items=" + items + "&buynow=" + buynow + "&point=" + point;
    });

    // ポイント設定したときの処理
    point_input.on("input", function (e) {

        // 入力されたポイント
        let InputPoint = new Decimal(String($(".buy-point__input").val()));

        // ポイントを金額に変換
        let PointToPrice = InputPoint.mul(per_point);

        // 請求額からポイントを減算
        let ViewPrice = total.sub(PointToPrice);

        amount_view.text(ViewPrice.toNumber().toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }));

        try {
            let player_balance_after = player_balance.sub(ViewPrice);
            $("#after_balance").text(player_balance_after.toNumber().toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }));
        } catch (TypeError) {
        }
        let point = new Decimal(amount_view.text()).mul(point_return)

        $("#get_point").text(point.toNumber().toLocaleString(undefined, {maximumFractionDigits: 2}));
    });
});
