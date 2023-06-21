window.onload = function() {
    const search = document.getElementById("search");
    const search_query = document.getElementById("search_query");
    const host = window.location.host;
    console.log(host)

    search.addEventListener('submit', function (e){
        e.preventDefault();
        let query = search_query.value;
        location.href=`//${host}/search/?q=${query}`;
    });
};

function close_expires(){
    document.getElementById("expires").style.display = "none";
}
