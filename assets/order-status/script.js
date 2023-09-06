$(function (){
    const progressBar = $(".progress-bar");
    let progress = 0;

    progress = progressBar.data("percent");
    progressBar.css("width",`${progress}%`);

    console.log(progress)
    if (progress >= 33 && progress < 66){
        $("#order2 .milestone-box").addClass("isActive");
        $("#order2 p").css("color", "#000");
    }else if (progress >= 66 && progress < 100){
        $("#order2 .milestone-box").addClass("isActive");
        $("#order3 .milestone-box").addClass("isActive");
        $("#order2 p").css("color", "#000");
        $("#order3 p").css("color", "#000");
    }else if (progress === 100){
        $("#order2 .milestone-box").addClass("isActive");
        $("#order3 .milestone-box").addClass("isActive");
        $("#order2 p").css("color", "#000");
        $("#order3 p").css("color", "#000");
        if (!$(".status-title div p").data("status")){
            $("#order4 .milestone-box").addClass("isActive");
            $("#order4 p").css("color", "#000");
        }
    }


});