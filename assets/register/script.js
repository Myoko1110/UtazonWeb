let balance;

let prideMonthly;
let prideYearly;
let total;
const redirectTo = new URL(window.location.href).searchParams.get("redirect");

$(function () {
    balance = new Decimal($("#player_balance").data("float"));
    prideMonthly = new Decimal($(".buy").data("monthly"));
    prideYearly = new Decimal($(".buy").data("yearly"));
    total = prideYearly;

    updateAfterBalance();
    updateTotal();

    $("#plan").on("change", function () {
        console.log($(this).val())
        if ($(this).val() === "monthly") {
            total = prideMonthly;
        } else {
            total = prideYearly;
        }
        updateAfterBalance();
        updateTotal();
    });

    $("#order_confirm").on("click", function (e) {
        plan = $("#plan").val()

        params = {
            plan: plan,
            redirect: redirectTo,
        }
        post("/pride/register/confirm/", params);
    });
});


function formatPrice(number) {
    return number.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}


function updateAfterBalance() {
    console.log(formatPrice(balance.sub(total).toNumber()))
    $("#after_balance").text(formatPrice(balance.sub(total).toNumber()));
}

function updateTotal(){
    $("#total").text(formatPrice(total.toNumber()));

    if (balance.toNumber() < total.toNumber()){
        $("#order_confirm").addClass("isInvalid");
    }else{
        $("#order_confirm").removeClass("isInvalid");
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