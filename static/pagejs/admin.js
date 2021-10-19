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
