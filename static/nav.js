$(window).resize(function() {
    var sidebar = document.getElementById('sidebar');
    var container = document.getElementsByClassName('container')[0];
    container.style.paddingLeft = 'calc(.75rem + ' + sidebar.offsetWidth + 'px)';
});
document.addEventListener("DOMContentLoaded", function(event){
    var sidebar = document.getElementById('sidebar');
    var container = document.getElementsByClassName('container')[0];
    container.style.paddingLeft = 'calc(.75rem + ' + sidebar.offsetWidth + 'px)';
})