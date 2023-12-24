$(document).ready(function () {
    const item_id = $(".review-title__item p").data("id");

    $("#submit").on('click', function () {
        amount = $("#text").val();
        params = {
            id: item_id,
            amount: amount,
        }

        post("post/", params);
    });
});

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
