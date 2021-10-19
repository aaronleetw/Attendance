var signaturePad, selPeriod, canvas, width = $(window).width(), modal;
function submitForm() {
    if (!signaturePad.isEmpty()) {
        $('#' + modal).modal('hide');
        loadingAnimation();
        signaturePad.off();
        var data = signaturePad.toDataURL('image/png');
        document.getElementById("attendanceData^" + selPeriod).getElementsByClassName("signatureData")[0].value = data;
        document.getElementById("attendanceData^" + selPeriod).submit();
    }
    else {
        alert("Please sign first");
    }
}
function resizeCanvas() {
    var ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);
    signaturePad.clear(); // otherwise isEmpty() might return incorrect value
}
function viewSignature(period) {
    selPeriod = period
    $('.viewSignatureBtn').attr({ 'disabled': 'disabled' });
    $('.viewSignatureBtn').removeClass('margin-bottom');
    modal = 'sign-' + period;
    $('#' + modal).modal('show');
    var cnt = 0;
    $('.tobeform').each(function (i, obj) {
        if ($(this).is(":checked")) {
            cnt++;
            $('#postHomeroomAbs').append('<input type="checkbox" name="' + $(this).attr('class').split(' ')[1].split('^')[1]
                + '" checked="checked">');
        }
    });
    if (cnt == 0) {
        $('#allPresentWarning-' + period).removeAttr('hidden');
    }
    canvas = document.getElementById("signature_pad^" + period);
    signaturePad = new SignaturePad(canvas);
    width = $(window).width();
    window.addEventListener("resize", () => {
        if (width != $(window).width()) {
            resizeCanvas();
            width = $(window).width();
        }
    });
    document.getElementById(modal).addEventListener("shown.bs.modal", function (e) {
        resizeCanvas();
    });
    resizeCanvas();
}
function unCheckAbs(string) {
    document.getElementById('absent^' + string).checked = false;
}
function unCheckLate(string) {
    document.getElementById('late^' + string).checked = false;
}

function loadingAnimation() {
    $("div.container").hide();
    $('#loading').show();
}
function chgDate(sel) {
    loadingAnimation();
    var url = '/manage/date/' + $('#date').val()
    var new_form = document.createElement('form');
    new_form.method = 'GET';
    new_form.action = url;
    document.body.appendChild(new_form);
    new_form.submit();
}
