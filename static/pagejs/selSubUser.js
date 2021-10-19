function loadingAnimation() {
    if ($('#subuser_form_sel').val == '')
        return;
    $('#subuser_form_sel').submit();
    $('.container').hide();
    $('#loading').show();
}
