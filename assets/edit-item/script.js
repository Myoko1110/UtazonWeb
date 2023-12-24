let new_image = [];
$(document).ready(function () {
    jQuery.trumbowyg.langs.ja = {
        viewHTML: "HTML表示",
        undo: "元に戻す",
        redo: "やり直す",
        formatting: "フォーマット",
        p: "本文",
        blockquote: "引用",
        code: "コード",
        header: "見出し",
        bold: "太字",
        italic: "斜体",
        strikethrough: "取り消し線",
        underline: "下線",
        strong: "太字",
        em: "斜体",
        del: "取り消し線",
        superscript: "上付き文字",
        subscript: "下付き文字",
        unorderedList: "箇条書き",
        orderedList: "段落番号",
        insertImage: "URLから画像を挿入",
        upload: "画像のアップロード",
        link: "リンク",
        createLink: "リンクの作成",
        unlink: "リンクの削除",
        justifyLeft: "左揃え",
        justifyCenter: "中央揃え",
        justifyRight: "右揃え",
        justifyFull: "両端揃え",
        horizontalRule: "横罫線",
        removeformat: "フォーマットの削除",
        fullscreen: "全画面表示",
        close: "閉じる",
        submit: "送信",
        reset: "キャンセル",
        required: "必須",
        description: "説明",
        title: "タイトル",
        text: "テキスト",
        target: "ターゲット",
        image: "画像"
    };
    $("#editor").trumbowyg({
        autogrow: true,
        btnsDef: {
            image: {
                dropdown: ['insertImage', 'upload'],
                ico: 'insertImage'
            }
        },
        lang: "ja",
        btns: [
            ['undo', 'redo'],
            ['formatting'],
            ['strong', 'em', 'del'],
            ['superscript', 'subscript'],
            ['link', 'image'],
            ['unorderedList', 'orderedList'],
            ['horizontalRule'],
            ['fullscreen'],
        ],
        plugins: {
            upload: {
                serverPath: '/post/upload/',
                fileFieldName: 'image',
            }
        }
    });
    const detail = $(".review-value__detail").data("html")
    if (detail !== "None"){
        $("#editor").trumbowyg("html", detail);
    }

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
        $(".review-value-1__list img").on("click", function () {
            $(this).parent().remove();
        });
    }


    const image = JSON.parse(decodeURIComponent($(".review-value__image").data("img")));
    const item_id = $(".review-title__item p").data("id");
    let update_image = image;
    const trash_svg = $(".review__about-value-1").data("svg");

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
            $(".review-value__detail").css("display", "none");

        }else if (tab === "画像") {
            $(".review-value__image").css("display", "block");

            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__about").css("display", "none");
            $(".review-value__keyword").css("display", "none");
            $(".review-value__item").css("display", "none");
            $(".review-value__detail").css("display", "none");

        }else if (tab === "説明") {
            $(".review-value__about").css("display", "block");
            $(".review-value__keyword").css("display", "block");

            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__image").css("display", "none");
            $(".review-value__item").css("display", "none");
            $(".review-value__detail").css("display", "none");

        }else if (tab === "詳細") {
            $(".review-value__detail").css("display", "block");

            $(".review-value__title").css("display", "none");
            $(".review-value__text").css("display", "none");
            $(".review-value__category").css("display", "none");
            $(".review-value__image").css("display", "none");
            $(".review-value__item").css("display", "none");
            $(".review-value__about").css("display", "none");
            $(".review-value__keyword").css("display", "none");

        }
    });

    $("#submit a").on('click', function () {
        $("#title_required").css("display", "none");
        $("#text_required").css("display", "none");
        $("#image_required").css("display", "none");
        $("#image_over").css("display", "none");
        $("#text_required").css("display", "none");
        $("#category_required").css("display", "none");
        $("#about_required").css("display", "none");

        let title = $("#title").val();
        let text = $("#text").val();

        let image_lengh = update_image.length + new_image.length;
        let selectedElements = $('.isSelect');

        let inputValues = [];
        $(".review__about-value-1 .review-value-1__list input").each(function () {
            inputValue = $(this).val();
            inputValues.push(inputValue);
        });

        if (title === "" || image_lengh > 5 || image_lengh === 0 || Number(text) === 0 || selectedElements.length !== 1 || selectedElements.length === 0 || inputValues[0] === "") {
            if (title === "") {
                $("#title_required").css("display", "block");
            }
            if (image_lengh === 0) {
                $("#image_required").css("display", "block");
            }
            if (image_lengh > 5) {
                $("#image_over").css("display", "block");
            }
            if (Number(text) === 0) {
                $("#text_required").css("display", "block");
            }
            if (selectedElements.length !== 1) {
                $("#category_required").css("display", "block");
            }
            if (selectedElements.length === 0) {
                $("#item_required").css("display", "block");
            }
            if (inputValues[0] === "") {
                $("#about_required").css("display", "block");
            }
            return;
        }

        let res = confirm("商品の情報を更新しますか？")
        if (!res){
            return;
        }

        let selectedCategory = selectedElements.data("en");

        let hostUrl = location.protocol + '//' + location.host + "/mypage/available/edit/post/";

        let params = {
            title: title,
            text: text,
            about: JSON.stringify(inputValues),
            update_image: JSON.stringify(update_image),
            category: selectedCategory,
            item_id: item_id,
            detail: $("#editor").trumbowyg("html")
        };
        for (let i = 0; i < new_image.length; i++) {
            params.new_image = new_image[i];
        }

        post(hostUrl, params);

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