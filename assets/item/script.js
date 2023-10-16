const xhr = new XMLHttpRequest();
const id = new URL(location.href).searchParams.get("id")
let cartNumber = 1;

let startTime;
let targetPosition;
let once = false;

const cookie = getCookieArray()
const blob = new Blob(cookie, {type: 'application/json'});
let stock = 0;

$(function () {
    targetPosition = $('.item-about__description-about').offset().top;
    stock = $(".item").data("stock");

    // アイテムの写真を切り替える
    $(".item-about__img-list-img").on("mouseenter", function () {
        src = $(this).data("src")
        $(".item-about__img-index-img").attr("src", src);
    });

    // 役に立ったを送信する
    $(".review-list__value-use-btn-useful").on("click", function (e) {
        e.preventDefault();
        xhr.open("GET", $(this).data("href"), true);
        xhr.send();

        $(this).parent().find("p").css("display", "block");
    });

    $(".item-about__buy-order-number-input").on("input", function () {
        cartNumber = $(this).val();
    });

    $(window).scroll(function () {
        initialize();
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
            if (cont_slide == 0) {
                dot.classList.add("isActive");
            }
            dots.append(dot);
            dot.addEventListener("click", () => {
                slideIndex = cont_slide + 1;
                slides.forEach((slide, cont_slide) => {
                    slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
                });
                for (var i = 1; i <= slides.length; i++) {
                    document.querySelector(`.index${i}`).classList.remove("isActive");
                }
                document.querySelector(`.index${slideIndex}`).classList.add("isActive");
            });
        });

        next.addEventListener("click", () => {
            slideIndex == slides.length ? (slideIndex = 1) : slideIndex++;
            slides.forEach((slide, cont_slide) => {
                slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
            });
            for (var i = 1; i <= slides.length; i++) {
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");

        });

        prev.addEventListener("click", () => {
            slideIndex == 1 ? (slideIndex = slides.length) : slideIndex--;
            slides.forEach((slide, cont_slide) => {
                slide.style = "left: -" + (slideIndex - 1) * 100 + "%;";
            });
            for (var i = 1; i <= slides.length; i++) {
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
            for (var i = 1; i <= slides.length; i++) {
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
            for (var i = 1; i <= slides.length; i++) {
                document.querySelector(`.index${i}`).classList.remove("isActive");
            }
            document.querySelector(`.index${slideIndex}`).classList.add("isActive");

            distX = null;
        });
    });

});
$(document).on('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
        update();
    }
});

function update() {
    if (once) {
        const duration = new Date(Date.now() - startTime);
        navigator.sendBeacon("/update_browsing_history/?item_id=" + id + "&duration=" + duration.getSeconds(), blob);
    }
}

function initialize() {
    if (targetPosition - $(window).height() < $(window).scrollTop() && !once) {
        once = true;
        startTime = Date.now();

        xhr.open("GET", "/initialize_browsing_history/?item_id=" + id, true);
        xhr.send();
    }
}

function getCookieArray() {
    let arr = [];
    if (document.cookie !== '') {
        let tmp = document.cookie.split('; ');
        for (let i = 0; i < tmp.length; i++) {
            let data = tmp[i].split('=');
            arr[data[0]] = decodeURIComponent(data[1]);
        }
    }
    return arr;
}

function buynow() {
    if (cartNumber == 0){
        $(".zero-invalid").css("display", "block");
        $(".item-about__buy-order-number-input").val(1);
        cartNumber = 1;
        setTimeout(function () {
            $(".zero-invalid").fadeOut(1000);
        }, 4000);

    } else if (cartNumber <= stock) {
        location.href = `../buy?item=%7B%22${id}%22%3A+${cartNumber}%7D`

    } else {
        $(".shortage").css("display", "block");
        $(".item-about__buy-order-number-input").val(stock);
        cartNumber = stock;
        setTimeout(function () {
            $(".shortage").fadeOut(1000);
        }, 4000);
    }
}

function cart(){
    if (cartNumber == 0){
        $(".zero-invalid").css("display", "block");
        $(".item-about__buy-order-number-input").val(1);
        cartNumber = 1;
        setTimeout(function () {
            $(".zero-invalid").fadeOut(1000);
        }, 4000);

    } else if (cartNumber <= stock) {
        location.href=`../cart/add/?id=${id}&qty=${cartNumber}`

    } else {
        $(".balloon").css("display", "block");
        $(".item-about__buy-order-number-input").val(stock);
        cartNumber = stock;
        setTimeout(function () {
            $(".balloon").fadeOut(1000);
        }, 4000);
    }
}
