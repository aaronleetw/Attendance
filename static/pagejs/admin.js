function getHR() {
    var grade = $('#sel-grade').val();
    $('#sel-room').html('<option value="">請先選擇年級</option>');
    if (grade === "") {
        $('#sel-room').attr('disabled', 'disabled')
        return
    }
    homerooms[grade].forEach(element => {
        $('#sel-room').append(`<option value="${element}">${element}</option>`)
    });
    $('#sel-room').removeAttr('disabled')
}
function redirAdmin() {
    if ($("#sel-room").val() == "") {
        alert("請選擇年級 / 班級！");
        return;
    }
    var url = "/manage/admin/" + $('#sel-grade').val() + "/" + $('#sel-room').val() + "/" + $('#date').val();
    var new_form = document.createElement('form');
    new_form.method = 'GET';
    new_form.action = url;
    document.body.appendChild(new_form);
    new_form.submit();
    $('.container').hide();
    $('#loading').show();
}

function edit(string) {
    $('.view-' + string).each(function (i, obj) {
        var num = $(this.firstElementChild).attr('class').split(' ')[2].replace('view-n-', '');
        if ($(this.firstElementChild).attr('class').split(' ')[1] == "n-1") {
            $(this).html("")
            $(this).append("<input type=\"checkbox\" class=\"tobeform 2^" + string + "^" + num + " late\" id=\"late^" + string + "^" + num + "\" onchange=\"unCheckAbs('" + string + "^" + num + "')\">");
            $(this).append("\n<input type=\"checkbox\" class=\"tobeform 1^" + string + "^" + num + " absent\" id=\"absent^" + string + "^" + num + "\" onchange=\"unCheckLate('" + string + "^" + num + "')\">");
        } else if ($(this.firstElementChild).attr('class').split(' ')[1] == "n-2") {
            $(this).html("")
            $(this).append("<input type=\"checkbox\" class=\"tobeform 2^" + string + "^" + num + " late\" id=\"late^" + string + "^" + num + "\" onchange=\"unCheckAbs('" + string + "^" + num + "')\">");
            $(this).append("\n<input type=\"checkbox\" class=\"tobeform 1^" + string + "^" + num + " absent\" id=\"absent^" + string + "^" + num + "\" onchange=\"unCheckLate('" + string + "^" + num + "')\" checked>");
        } else if ($(this.firstElementChild).attr('class').split(' ')[1] == "n-3") {
            $(this).html("")
            $(this).append("<input type=\"checkbox\" class=\"tobeform 2^" + string + "^" + num + " late\" id=\"late^" + string + "^" + num + "\" onchange=\"unCheckAbs('" + string + "^" + num + "')\" checked>");
            $(this).append("\n<input type=\"checkbox\" class=\"tobeform 1^" + string + "^" + num + " absent\" id=\"absent^" + string + "^" + num + "\" onchange=\"unCheckLate('" + string + "^" + num + "')\">");
        }
    });
    $('#btns-' + string).html("")
    $('.afterSelButton').attr('disabled', 'disabled');
    $('#btns-' + string).append("<button class=\"btn btn-secondary editSaveButton\" onclick=\"afterSelAbs('" + string + "', 'edit')\">Save</button>");
}

function unCheckLate(string) {
    document.getElementById('late^' + string).checked = false;
}
function unCheckAbs(string) {
    document.getElementById('absent^' + string).checked = false;
}

function afterSelAbs(period) {
    $('#postHomeroomAbs #HR-period').attr('value', period);
    $('.tobeform').attr('disabled', 'disabled');
    $('.afterSelButton').attr('disabled', 'disabled');
    $('.tobeform').each(function (i, obj) {
        if ($(this).attr('class').split(' ')[1].split('^')[1] == period &&
            $(this).is(":checked")) {
            $('#postHomeroomAbs').append('<input type="checkbox" name="' + $(this).attr('class').split(' ')[1].split('^')[0] + '^'
                + $(this).attr('class').split(' ')[1].split('^')[2]
                + '" checked="checked">');
        }
    });
    $('#finalCheck').modal('show');
}

function submitForm() {
    $('#HR-notes').attr('value', $('#subjectNotes').val());
    $('#postHomeroomAbs').submit();
    $('#finalCheck').modal('hide');
    $('.container').hide();
    $('#loading').show();
}