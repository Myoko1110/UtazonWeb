const xhr = new XMLHttpRequest();
const star_invalid = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMzgiIGhlaWdodD0iMzUiPjxkZWZzPjxwYXRoIGlkPSJhIiBkPSJNMTkgMGwtNS44NyAxMS41MkwwIDEzLjM3bDkuNSA4Ljk3TDcuMjYgMzUgMTkgMjkuMDIgMzAuNzUgMzVsLTIuMjQtMTIuNjYgOS41LTguOTctMTMuMTMtMS44NXoiLz48L2RlZnM+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48dXNlIGZpbGw9IiNGRkYiIHhsaW5rOmhyZWY9IiNhIi8+PHBhdGggc3Ryb2tlPSIjQTI2QTAwIiBzdHJva2Utb3BhY2l0eT0iLjc1IiBkPSJNMTkgMS4xbC01LjU0IDEwLjg4TDEuMSAxMy43Mmw4Ljk0IDguNDRMNy45MiAzNC4xIDE5IDI4LjQ2bDExLjA4IDUuNjQtMi4xMS0xMS45NCA4Ljk0LTguNDQtMTIuMzYtMS43NEwxOSAxLjF6Ii8+PC9nPjwvc3ZnPg=="
const star_valid = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMzgiIGhlaWdodD0iMzUiPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iYSIgeDE9IjUwJSIgeDI9IjUwJSIgeTE9IjI3LjY1JSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkNFMDAiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNGRkE3MDAiLz48L2xpbmVhckdyYWRpZW50PjxwYXRoIGlkPSJiIiBkPSJNMTkgMGwtNS44NyAxMS41MkwwIDEzLjM3bDkuNSA4Ljk3TDcuMjYgMzUgMTkgMjkuMDIgMzAuNzUgMzVsLTIuMjQtMTIuNjYgOS41LTguOTctMTMuMTMtMS44NXoiLz48L2RlZnM+PGcgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48dXNlIGZpbGw9InVybCgjYSkiIHhsaW5rOmhyZWY9IiNiIi8+PHBhdGggc3Ryb2tlPSIjQTI2QTAwIiBzdHJva2Utb3BhY2l0eT0iLjc1IiBkPSJNMTkgMS4xbC01LjU0IDEwLjg4TDEuMSAxMy43Mmw4Ljk0IDguNDRMNy45MiAzNC4xIDE5IDI4LjQ2bDExLjA4IDUuNjQtMi4xMS0xMS45NCA4Ljk0LTguNDQtMTIuMzYtMS43NEwxOSAxLjF6Ii8+PC9nPjwvc3ZnPg=="
const params = new URL(window.location.href).searchParams;

let send_available = true;

var review = 0
$(function () {
    $("#star_1").on('click', function () {
        $("#star_1").attr("src", star_valid);
        $("#star_2").attr("src", star_invalid);
        $("#star_3").attr("src", star_invalid);
        $("#star_4").attr("src", star_invalid);
        $("#star_5").attr("src", star_invalid);
        review = 1;
        send_star(1)
    });
    $("#star_2").on('click', function () {
        $("#star_1").attr("src", star_valid);
        $("#star_2").attr("src", star_valid);
        $("#star_3").attr("src", star_invalid);
        $("#star_4").attr("src", star_invalid);
        $("#star_5").attr("src", star_invalid);
        review = 2;
        send_star(2)
    });
    $("#star_3").on('click', function () {
        $("#star_1").attr("src", star_valid);
        $("#star_2").attr("src", star_valid);
        $("#star_3").attr("src", star_valid);
        $("#star_4").attr("src", star_invalid);
        $("#star_5").attr("src", star_invalid);
        review = 3;
        send_star(3)
    });
    $("#star_4").on('click', function () {
        $("#star_1").attr("src", star_valid);
        $("#star_2").attr("src", star_valid);
        $("#star_3").attr("src", star_valid);
        $("#star_4").attr("src", star_valid);
        $("#star_5").attr("src", star_invalid);
        review = 4;
        send_star(4)
    });
    $("#star_5").on('click', function () {
        $("#star_1").attr("src", star_valid);
        $("#star_2").attr("src", star_valid);
        $("#star_3").attr("src", star_valid);
        $("#star_4").attr("src", star_valid);
        $("#star_5").attr("src", star_valid);
        review = 5;
        send_star(5)
    });
    $("#submit").on('click', function () {
        title = $("#title").val();
        text = $("#text").val();
        console.log(text)
        if (title === "" || text === "" || review === 0) {
            if (title === "") {
                $("#title_required").css("display", "block");
            }
            if (text === "") {
                $("#text_required").css("display", "block");
            }
            if (review === 0) {
                $("#star_required").css("display", "block");
            }
            return false;
        }

        location.href = `/review/post/?id=${params.get('id')}&star=${review}&title=${title}&text=` + encodeURIComponent(text)
    });

    review = $("img.isActive").data("star");
    $(`#star_${review}`).click();
});

function send_star(star){
    if (send_available) {
        xhr.open("GET", `/review/star/?id=${params.get('id')}&star=${star}`, true);
        xhr.send();

        $(".review-value__star p").css("display", "block");
        time_deley().then(r => function (){});
    }
}

async function time_deley(){
    send_available = false;
    setTimeout(function (){
        send_available = true;
    }, 1000);
}