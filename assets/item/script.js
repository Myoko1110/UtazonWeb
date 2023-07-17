const xhr = new XMLHttpRequest();
const host = `http://${location.host}`;
let cart_number = 1;

$(function (){

    // アイテムの写真を切り替える
    $(".item-about__img-list-img").on("mouseenter", function (){
        src = $(this).data("src")
        $(".item-about__img-index-img").attr("src", src);
    });

    // 役に立ったを送信する
    $(".review-list__value-use-btn-useful").on("click", function (e){
        e.preventDefault();
        let link = $(this).data("href");

        xhr.open("GET", host + $(this).data("href"), true);
        xhr.send();

        $(`a[data-href="${link}"]`).css("display", "none");
        $(`p[data-href="${link}"]`).css("display", "block");
    });

    // カートに追加するアイテム数を変更
    $('#card_add').on("input", function() {
    cart_number = $(this).val();
  });

});