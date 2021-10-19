function loadingAnimation() {
    // if csv is empty
    if ($("#csv").val() == "") {
        alert("Please select a file!");
        return;
    }
    $('#uploadCsvForm').submit();
    $('.container').hide();
    $('#loading').show();
}
