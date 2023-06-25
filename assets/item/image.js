$(function (){
    $("#image_1").on("mouseenter", function(event) {
        src = $(this).attr("src");
        $(".item-about__img-index-img").attr("src", src);
    });
    $("#image_2").on("mouseenter", function(event) {
        src = $(this).attr("src");
        $(".item-about__img-index-img").attr("src", src);
    });
    $("#image_3").on("mouseenter", function(event) {
        src = $(this).attr("src");
        $(".item-about__img-index-img").attr("src", src);
    });


})