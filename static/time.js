(function () {
    function checkTime(i) {
        return (i < 10) ? "0" + i : i;
    }

    function startTime() {
        var today = new Date(),
            y = today.getFullYear(),
            mm = checkTime(today.getMonth() + 1),
            d = checkTime(today.getDate()),
            h = checkTime(today.getHours()),
            m = checkTime(today.getMinutes()),
            s = checkTime(today.getSeconds());
        document.getElementById('showTime').innerHTML = y + "/" + mm + "/" + d + " " + h + ":" + m + ":" + s;
        t = setTimeout(function () {
            startTime()
        }, 500);
    }
    startTime();
})();
$(window).resize();
$(window).scroll();