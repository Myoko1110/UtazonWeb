let new_image = [];
$(document).ready(function () {
    function addImageHoverHandlers() {
        $(".review-value-1 .image").hover(
            function () {
                $(this).addClass("isActive");
            },
            function () {
                $(this).removeClass("isActive");
            }
        );

        $(".review-value-1 .image").on("click", function () {
            imgUrl = $(this).find("img").attr("src");
            $(this).remove();
            update_image = update_image.filter(fruit => fruit !== imgUrl);
            new_image = new_image.filter(fruit => fruit !== imgUrl);

            if ($(".review-value-1").children().length < 5) {
                $(".review-value-2").css("display", "block")
            }
        });
    }


    const image = $(".review-value__image").data("img");
    const item_id = $(".review-title__item p").data("id");
    const mc_uuid = $(".review-title__item p").data("uuid");
    let update_image = image;

    let imageElement = "";
    for (let i in image) {
        let element = `<div class="image"><img src="${image[i]}"></div>`;
        imageElement += element;
    }
    $(".review-value-1").html(imageElement)
    addImageHoverHandlers()

    document.querySelector(".fileAdd").addEventListener("click", () => {
        document.querySelector(".fileAdd input").click();
    });
    $("#fileInput").on("change", function () {
        var fileReader = new FileReader();
        fileReader.onload = (function () {
            src = fileReader.result;

            imageElement = `<div class="image"><img src="${src}"></div>`;
            $(".review-value-1").append(imageElement);

            if ($(".review-value-1").children().length >= 5) {
                $(".review-value-2").css("display", "none")
            }
            new_image.push(src);
            addImageHoverHandlers()
        });
        fileReader.readAsDataURL(this.files[0]);
    });
    $("#submit").on('click', function () {
        title = $("#title").val();
        text = $("#text").val();

        image_lengh = update_image.length + new_image.length;

        if (title === "" || text === "" || image_lengh === 0) {
            if (title === "") {
                $("#title_required").css("display", "block");
            }
            if (text === "") {
                $("#text_required").css("display", "block");
            }
            if (image_lengh === 0) {
                $("#image_required").css("display", "block");
            }

            return false;
        }

        var hostUrl = location.protocol + '//' + location.host + "/mypage/on_sale/edit/post/";

        // 画像のアップロード処理を行う
        var formData = new FormData();
        formData.append('item_id', item_id);
        formData.append('mc_uuid', mc_uuid);
        formData.append('title', title);
        formData.append('text', text);
        formData.append("update_image", JSON.stringify(update_image))

        // 新しい画像を追加
        for (let i = 0; i < new_image.length; i++) {
            const base64Data = new_image[i]
            formData.append('new_image', base64Data); // ファイル名も指定
        }

        $.ajax({
            type: 'POST',
            url: hostUrl,
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                location.href = `/mypage/on_sale/`;
            },
            error: function (error) {
                $("#cnxError").css("display", "block");
            }
        });
    });
});
