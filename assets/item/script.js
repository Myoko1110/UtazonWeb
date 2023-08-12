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

    $('#card_add').on("input", function() {
        cart_number = $(this).val();
    });

    // カルーセル
    const sliders = document.querySelectorAll(".item-about__img-slider");
    sliders.forEach((slider, cont_slider) => {
        let slideIndex = 1;
        let slides = slider.querySelectorAll(".item-about__img-slide");
        let prev = document.createElement("span");
        prev.classList.add("prev-001");
        prev.innerHTML = "&#10094;";
        slider.append(prev);
        let next = document.createElement("span");
          next.classList.add("next-001");
        next.innerHTML = "&#10095;";
        slider.append(next);

        let dots = document.createElement("div");
        dots.classList.add("dots");
        slider.append(dots);

        slides.forEach((slide, cont_slide) => {
            let dot = document.createElement("span");
            dot.classList.add("dot");
            dot.classList.add(`index${cont_slide + 1}`);
            if(cont_slide == 0){
                dot.classList.add("isActive");
            }
            dots.append(dot);
            dot.addEventListener("click", (e) => {
                slideIndex = cont_slide + 1;
                slides.forEach((slide, cont_slide) => {
                    slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
                });
                for(var i = 1; i <= slides.length; i++){
                    document.querySelector(`.index${i}`).classList.remove("isActive");
                }
                document.querySelector(`.index${slideIndex}`).classList.add("isActive");
            });
        });

        next.addEventListener("click", (e) => {
            slideIndex == slides.length ? (slideIndex = 1) : slideIndex++;
            slides.forEach((slide, cont_slide) => {
                slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
            });
            for(var i = 1; i <= slides.length; i++){
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");

        });

        prev.addEventListener("click", (e) => {
            slideIndex == 1 ? (slideIndex = slides.length) : slideIndex--;
            slides.forEach((slide, cont_slide) => {
                slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
            });
            for(var i = 1; i <= slides.length; i++){
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");
        });
        slider.addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
        });

        slider.addEventListener("touchmove", (e) => {
            if (!startX) return;

            distX = e.touches[0].clientX - startX;

            slides.forEach((slide) => {
                slide.style.transition = "none";
                slide.style.left = `calc(-${(slideIndex - 1) * 100}% + ${distX}px)`;
            });
            for(var i = 1; i <= slides.length; i++){
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");
        });

        slider.addEventListener("touchend", () => {
            if (!distX) return;

            if (Math.abs(distX) > 50) {
                if (distX > 0) {
                    slideIndex = slideIndex === 1 ? slides.length : slideIndex - 1;
                } else {
                    slideIndex = slideIndex === slides.length ? 1 : slideIndex + 1;
                }
            }

            slides.forEach((slide) => {
                slide.style.transition = "";
                slide.style.left = `-${(slideIndex - 1) * 100}%`;
            });
            for(var i = 1; i <= slides.length; i++){
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");

            distX = null;
        });
    });
});
