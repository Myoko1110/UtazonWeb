function on_delete(obj) {
    id = $(obj).data("id");
    $("#delete a").attr("href", `delete/?id=${id}`)
    $("#delete").css("display", "flex");
}