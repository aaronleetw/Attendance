var signaturePad, hrCfrm = false, canvas = document.getElementById("signature_pad");
var width = $(window).width();
function loadingAnimation() {
    $('.container').hide();
    $('#loading').show();
}
function chgDate() {
    loadingAnimation();
    var url = '/manage/date/' + $('#date').val()
    var new_form = document.createElement('form');
    new_form.method = 'GET';
    new_form.action = url;
    document.body.appendChild(new_form);
    new_form.submit();
}
function submitForm() {
    if (!signaturePad.isEmpty()) {
        $('#finalCheck').modal('hide');
        loadingAnimation();
        signaturePad.off();
        var data = signaturePad.toDataURL('image/png');
        if (hrCfrm) {
            $('#hrCfrm-sign').val(data);
            $('#hrCfrm-notes').val($('#subjectNotes').val());
            document.getElementById('homeroom_confirm').submit()
        } else {
            var notes = $('#subjectNotes').val();
            document.getElementById('HR-signatureData').value = data;
            document.getElementById('HR-notes').value = notes;
            document.getElementById('postHomeroomAbs').submit();
        }
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
function showSignaturePad() {
    $('#finalCheck').modal('show');
    signaturePad = new SignaturePad(canvas);
    width = $(window).width();
    window.addEventListener("resize", () => {
        if (width != $(window).width()) {
            resizeCanvas();
            width = $(window).width();
        }
    });
    document.getElementById("finalCheck").addEventListener('shown.bs.modal', function (e) {
        resizeCanvas();
    });
    resizeCanvas();
}
function afterSelAbs(period) {
    var tobeformArr = [];
    $('#postHomeroomAbs #HR-period').attr('value', period);
    $('.tobeform').attr('disabled', 'disabled');
    $('.afterSelButton').attr('disabled', 'disabled');
    $('#showSignPeriod').text(period);
    $('#showSignSubjectName').text(periodData[period]);
    var cnt = 0;
    $('.tobeform').each(function (i, obj) {
        if ($(this).attr('class').split(' ')[1].split('^')[1] == period &&
            $(this).is(":checked")) {
            cnt++;
            $('#postHomeroomAbs').append('<input type="checkbox" name="' + $(this).attr('class').split(' ')[1].split('^')[0] + '^'
                + $(this).attr('class').split(' ')[1].split('^')[2]
                + '" checked="checked">');
        }
    });
    if (cnt == 0) {
        $('#allPresentWarning').removeAttr('hidden');
    }
    // show signature pad
    showSignaturePad()
}
function homeroomCfrm() {
    hrCfrm = true;
    $('#showSignPeriod').text("HOMEROOM CONFIRM");
    $('#showSignSubjectName').text("班導確認");
    $('.tobeform').attr('disabled', 'disabled');
    $('.afterSelButton').attr('disabled', 'disabled');
    showSignaturePad();
}
function unCheckLate(string) {
    document.getElementById('late^' + string).checked = false;
}
function unCheckAbs(string) {
    document.getElementById('absent^' + string).checked = false;
}
