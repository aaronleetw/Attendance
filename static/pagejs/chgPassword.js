function validateEmail(email) {
    const emailRegEx = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    function loadingAnimation() {
        $('#loginForm').submit();
        if ($("#username").val() == "" || $("#password").val() == "" || $("#new_username").val() == "" || $("#new_password").val() == "" ||
            !emailRegEx.test($("#username").val().toLowerCase()) || !emailRegEx.test($("#new_username").val().toLowerCase())) {
            return;
        }
        $('.container').hide();
        $('#loading').show();
    }
}

function password_show_hide(num) {
    var x = '';
    var show_eye = '';
    var hide_eye = '';
    if (num == 1) {
        x = document.getElementById("password");
        show_eye = document.getElementById("old_show_eye");
        hide_eye = document.getElementById("old_hide_eye");
    }
    else {
        x = document.getElementById("new_password");
        show_eye = document.getElementById("new_show_eye");
        hide_eye = document.getElementById("new_hide_eye");
    }
    hide_eye.classList.remove("d-none");
    if (x.type === "password") {
        x.type = "text";
        show_eye.style.display = "none";
        hide_eye.style.display = "block";
    } else {
        x.type = "password";
        show_eye.style.display = "block";
        hide_eye.style.display = "none";
    }
}
