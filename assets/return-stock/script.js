$(document).ready(function () {
    const item_id = $(".review-title__item p").data("id");

    $("#submit").on('click', function () {
        amount = $("#text").val();

        location.href = `post/?id=${item_id}&amount=${amount}`
    });
});
