var signaturePad, selPeriod, canvas, width = $(window).width(), modal;
var indDS = {};
function submitForm() {
    if (!signaturePad.isEmpty()) {
        for (var i in indDS) {
            var tmp = document.createElement('input');
            tmp.type = 'hidden';
            tmp.name = 'ds^' + i;
            tmp.value = indDS[i];
            document.getElementById('attendanceData^' + selPeriod).appendChild(tmp);
        }
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
function unCheckLate(string) {
    document.getElementById('late^' + string).checked = false;
    strForNote = string.substring(string.indexOf("^") + 1);
    if (document.getElementById("absent^" + string).checked == true && !!!document.getElementById("note^"+strForNote)) {
        var tmp = document.createElement('input')
        tmp.type = 'text'
        tmp.id = 'note^'+strForNote
        tmp.name = 'note^'+strForNote
        tmp.className = 'form-control'
        document.getElementById('input^' + string).appendChild(tmp)
    } else if (document.getElementById("absent^" + string).checked == false) {
        document.getElementById('note^' + strForNote).remove();
    }

}
function unCheckAbs(string) {
    document.getElementById('absent^' + string).checked = false;
    strForNote = string.substring(string.indexOf("^") + 1);
    if (document.getElementById("late^" + string).checked == true && !!!document.getElementById("note^"+strForNote)) {
        var tmp = document.createElement('input')
        tmp.type = 'text'
        tmp.id = 'note^'+strForNote
        tmp.name = 'note^'+strForNote
        tmp.className = 'form-control'
        document.getElementById('input^' + string).appendChild(tmp)
    } else if (document.getElementById("late^" + string).checked == false) {
        document.getElementById('note^' + strForNote).remove();
    }
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
function addDS() {
    if ($('#dsnumbersel').val() == "" || $('#dsoffensesel').val() == "") {
        return;
    }
    var text = $('#dsoffensesel').val()
    if ($('#dsoffenseother').val() != "") {
        text = text.concat(": ", $('#dsoffenseother').val());
    }
    indDS[$("#dsnumbersel").val()] = text;
    $('#inddsview>.col').append('<div class="row"><div class="col">'+$("#dsnumbersel").val()+'</div><div class="col">'+text+'</div></div>')
    $('#dsnumbersel option[value="'+$("#dsnumbersel").val()+'"]').remove();
    $('#dsoffenseother').val("");
    $('#dsoffensesel').val("");
    $('#dsnumbersel').val("");
}