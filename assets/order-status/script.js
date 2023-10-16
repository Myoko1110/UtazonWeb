let progress = 0;
$(function () {
    const progressBar = $(".status-bar__obj-valid");

    progress = progressBar.data("percent");
    progressBar.css("height", `${progress}%`);

    $("#order_1 .check_list p").css("color", "#000");
    $("#order_1 .check_box").addClass("isActive");

    if (progress >= 33) {
        if ($(".status-title div p").data("ship") === "True") {
            $("#order_2 .check_list p").css("color", "#000");
            $("#order_2 .check_box").addClass("isActive");
        }
    }
    if (progress >= 66) {
        if ($(".status-title div p").data("ship") === "True") {
            $("#order_3 .check_list p").css("color", "#000");
            $("#order_3 .check_box").addClass("isActive");
        }
    }
    if (progress === 100.0) {
        if ($(".status-title div p").data("ship") === "True" && $(".status-title div p").data("status") === "False") {
            $("#order_4 .check_list p").css("color", "#000");
            $("#order_4 .check_box").addClass("isActive");
        }
    }


});