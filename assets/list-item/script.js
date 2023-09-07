let new_image = [];
$(document).ready(function(){
    function addImageHoverHandlers() {
        $(".review-value-1 .image").hover(
            function () {
                $(this).addClass("isActive");
            },
            function () {
                $(this).removeClass("isActive");
            }
        );

        $(".review-value-1 .image").on("click", function (){
            imgUrl = $(this).find("img").attr("src");
            $(this).remove();
            update_image = update_image.filter(fruit => fruit !== imgUrl);
            new_image = new_image.filter(fruit => fruit !== imgUrl);

            if ($(".review-value-1").children().length < 5){
                $(".review-value-2").css("display", "block")
            }
        });
        $(".review-value-1__list img").on("click", function (){
            $(this).parent().remove();
        });
    }

    const trash_svg = $(".review__about-value-1").data("svg");
    const item_id = $(".review-title__item p").data("id");
    const mc_uuid = $(".review-title__item p").data("uuid");

    document.querySelector(".fileAdd").addEventListener("click", () => {
        document.querySelector(".fileAdd input").click();
    });
    $("#fileInput").on("change", function(){
        var fileReader = new FileReader();
        fileReader.onload = (function() {
            src = fileReader.result;

            imageElement = `<div class="image"><img src="${src}"></div>`;
            $(".review-value-1").append(imageElement);

            if ($(".review-value-1").children().length >= 5){
                $(".review-value-2").css("display", "none")
            }
            new_image.push(src);
            addImageHoverHandlers();
        });
        fileReader.readAsDataURL(this.files[0]);
    });
    $(".review__about-value-2").on("click", function (){
        $(".review__about-value-1").append(`<div class="review-value-1__list"> <input type="text"><img src="${trash_svg}"></div>`)
        addImageHoverHandlers();
    });
    $(".category-list div").on("click", function (){
        ul = $(this).parent().find("ul");

        if (ul.css("display") === "none"){
            ul.css("display", "block");
        }else{
            ul.css("display", "none");
        }
    });
    $(".category-child_li").on("click", function (){
       $(".isSelect").removeClass("isSelect");
       $(this).addClass("isSelect");
    });

    $("#submit").on('click', function (){
        title = $("#title").val();
        text = $("#text").val();

        image_lengh = new_image.length;

        if (title === "" || new_image.length === 0){
            if (title === ""){
                $("#title_required").css("display", "block");
            }
            if (text === ""){
                $("#text_required").css("display", "block");
            }
            if(image_lengh === 0){
                $("#image_required").css("display", "block");
            }

            return;
        }

        var selectedElements = $('.isSelect');
        if (selectedElements !== 1){
            $("#category_required").css("display", "block");
        }
       var category = selectedElements.data("en");

        var hostUrl= location.protocol + '//' + location.host + "/mypage/list_item/post/";
        var inputValues = [];
        $(".review__about-value-1 .review-value-1__list input").each(function() {
            var inputValue = $(this).val();
            inputValues.push(inputValue);
        });
        console.log(inputValues)
        if (inputValues[0] === ""){
            $("#about_required").css("display", "block");
            return;
        }

        params = {title: title, text: text, about: JSON.stringify(inputValues), category: category}
        for (let i = 0; i < new_image.length; i++) {
                params.new_image = new_image[i];
        }
        post(hostUrl, params);

    });
});


function post(path, params, method='post') {

  // The rest of this code assumes you are not using a library.
  // It can be made less wordy if you use one.
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