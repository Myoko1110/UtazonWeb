let new_image = [];
$(document).ready(function () {

    // 更新用
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
            let imgUrl = $(this).find("img").attr("src");
            $(this).remove();
            new_image = new_image.filter(fruit => fruit !== imgUrl);

            if ($(".review-value-1").children().length < 5) {
                $(".review-value-2").css("display", "block")
            }
        });
        $(".review-value-1__list img").on("click", function () {
            $(this).parent().remove();
        });
    }

    // 初期設定
    const trash_svg = $(".review__about-value-1").data("svg");

    // ファイル選択
    document.querySelector(".fileAdd").addEventListener("click", () => {
        document.querySelector(".fileAdd input").click();
    });

    // ファイルアップロード
    $("#fileInput").on("change", function () {
        $("#image_size").css("display", "none");

        // 選択されたファイルの数を取得
        const fileCount = this.files.length;

        if (fileCount !== 1) {
            return;
        }

        const fileSize = this.files[0].size;

        if (fileSize > 2 * 1024 * 1024) {
            $("#image_size").css("display", "block");
            return;
        }

        let fileReader = new FileReader();
        fileReader.onload = (function () {
            const src = fileReader.result;

            const imageElement = `<div class="image"><img src="${src}"></div>`;
            $(".review-value-1").append(imageElement);

            if ($(".review-value-1").children().length >= 5) {
                $(".review-value-2").css("display", "none")
            }
            new_image.push(src);
            addImageHoverHandlers();
        });
        fileReader.readAsDataURL(this.files[0]);
    });

    // 概要追加
    $(".review__about-value-2").on("click", function () {
        $(".review__about-value-1").append(`<div class="review-value-1__list"><input type="text"><img src="${trash_svg}"></div>`)
        addImageHoverHandlers();
    });

    // カテゴリーの開閉
    $(".category-list div").on("click", function () {
        ul = $(this).parent().find("ul");

        if (ul.css("display") === "none") {
            ul.css("display", "block");
        } else {
            ul.css("display", "none");
        }
    });

    // カテゴリーの選択
    $(".category-child_li").on("click", function () {
        $(".isSelect").removeClass("isSelect");
        $(this).addClass("isSelect");
    });

    // アイテムの選択
    $(".muci-slot div").on("click", function () {
        $(this).toggleClass("isSelectIndex");
    });

    $(".review-nav li").on("click", function (){
        let tab = $(this).text();
        $(".review-nav li").removeClass("isActive");
        $(this).addClass("isActive");

        if (tab === "出品情報") {
            $(".review-value__title").css("display", "block");
            $(".review-value__text").css("display", "block");
            $(".review-value__category").css("display", "block");

            $(".review-value__image").css("display", "none");
            $(".review-value__about").css("display", "none");
            $(".review-value__keyword").css("display", "none");
            $(".review-value__item").css("display", "none");

        }else if (tab === "画像") {
            $(".review-value__image").css("display", "block");
            
            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__about").css("display", "none");
            $(".review-value__keyword").css("display", "none");
            $(".review-value__item").css("display", "none");

        }else if (tab === "説明") {
            $(".review-value__about").css("display", "block");
            $(".review-value__keyword").css("display", "block");

            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__image").css("display", "none");
            $(".review-value__item").css("display", "none");

        }else if (tab === "アイテム") {
            $(".review-value__item").css("display", "block");

            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__image").css("display", "none");
            $(".review-value__about").css("display", "none");
            $(".review-value__keyword").css("display", "none");
        }
    })

    // 次へ
    $("#next").on("click", function (){
        $("#title_required").css("display", "none");
        $("#text_required").css("display", "none");
        $("#image_required").css("display", "none");
        $("#image_over").css("display", "none");
        $("#text_required").css("display", "none");
        $("#category_required").css("display", "none");
        $("#about_required").css("display", "none");

        let item_name = $("#title").val();
        let item_price = $("#text").val();
        let keyword = $("#keyword").val();

        let image_length = new_image.length;
        let selectedCategory = $('.isSelect');
        let selectedItems = $(".isSelectIndex");

        let inputValues = [];
        $(".review__about-value-1 .review-value-1__list input").each(function () {
            const inputValue = $(this).val();
            inputValues.push(inputValue);
        });

        if (item_name === "" || image_length > 5 || image_length === 0 || Number(item_price) === 0 || selectedCategory.length !== 1 || selectedItems.length === 0 || keyword.length > 150) {
            if (item_name === "") {
                $("#title_required").css("display", "block");
            }
            if (image_length === 0) {
                $("#image_required").css("display", "block");
            }
            if (image_length > 5) {
                $("#image_over").css("display", "block");
            }
            if (Number(item_price) === 0) {
                $("#text_required").css("display", "block");
            }
            if (selectedCategory.length !== 1) {
                $("#category_required").css("display", "block");
            }
            if (selectedCategory.length === 0) {
                $("#item_required").css("display", "block");
            }
            if (inputValues[0] === "") {
                $("#about_required").css("display", "block");
            }
            if (keyword.length > 150) {
                $("#keyword_over").css("display", "block");
            }
            $("#nextError").css("display", "block");
            return;
        }

        $(".product").css("display", "none");
        $(".caution").css("display", "block");
        $(window).scrollTop(0);
    });

    $("#return").on("click", function (){
        $(".product").css("display", "block");
        $(".caution").css("display", "none");
        $(window).scrollTop(0);
    });

    // 送信
    $("#submit").on('click', function () {

        let item_name = $("#title").val();
        let item_price = $("#text").val();
        let keyword = $("#keyword").val();

        let selectedCategory = $('.isSelect');
        let selectedItems = $(".isSelectIndex");

        let inputValues = [];
        $(".review__about-value-1 .review-value-1__list input").each(function () {
            const inputValue = $(this).val();
            inputValues.push(inputValue);
        });

        let category = selectedCategory.data("en");
        let hostUrl = location.protocol + '//' + location.host + "/mypage/list_item/post/";

        const item0 = selectedItems.eq(0);

        let isAllSame = false;
        let indexList = [];
        selectedItems.each(function() {
            if ($(this).data("namespacedkey") !== item0.data("namespacedkey")){
                isAllSame = true;
            }
            if ($(this).data("amount") !== item0.data("amount")){
                isAllSame = true;
            }
            if (JSON.stringify($(this).data("enchantment")) !== JSON.stringify(item0.data("enchantment"))){
                isAllSame = true;
            }
            if ($(this).data("damage") !== item0.data("damage")){
                isAllSame = true;
            }
            let dataIndex = $(this).data("index");
            indexList.push(dataIndex);
        });
        if (isAllSame){
            $("#item_same").css("display", "block");
            return;
        }

        let res = confirm("商品を出品しますか？")
        if (!res){
            return;
        }

        let params = {
            title: item_name,
            text: item_price,
            about: JSON.stringify(inputValues),
            category: category,
            items: JSON.stringify(indexList),
            keyword: keyword
        };
        for (let i = 0; i < new_image.length; i++) {
            params.new_image = new_image[i];
        }

        post(hostUrl, params);

    });
});


function post(path, params, method = 'post') {
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