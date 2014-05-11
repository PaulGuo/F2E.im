$(function () {
    var $uploadPictureForm = $('.upload-picture-form');
    $uploadPictureForm.change(function (e) {
        console.log(e);
        $uploadPictureForm.submit();
    });
    var $editor = $("form textarea[name=content]");
    window.uploadImageCallback = function (pictureKeys) {
        console.log(pictureKeys);
        _.each(pictureKeys, function (pic) {
            console.log(pic);
            var text = "![" + pic['url'] + "](" + pic['url'] + ")";
            $editor.html($editor.html() + text);
        });
    };
    $('.upload-picture-btn').click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        $uploadPictureForm.find('[type=file]').trigger('click');
    });
});