<!-- add.jinja2 or edit.jinja2 -->
{% extends "admin/layout/default.jinja2" %}

{% block javascript %}
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.5/jquery.validate.min.js?v={{configs.basic.version}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.19.5/additional-methods.min.js?v={{configs.basic.version}}"></script>
<script src="/static/assets/js/backend/%%js_file_name%%.js"></script>
<script src="/static/assets/js/backend/upload.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/tinymce/7.0.0/tinymce.min.js"
    integrity="sha512-xEHlM+pBhSw2P/G+5x3BR8723QPEf2bPr4BLV8p8pvtaCHmWVuSzzKy9M0oqWaXDZrB3r2Ntwmc9iJcNV/nfBQ=="
    crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/flatpickr.min.js"
    integrity="sha512-K/oyQtMXpxI4+K0W7H25UopjM8pzq0yrVdFdG21Fh5dBe91I40pDd9A4lzNlHPHBIP2cwZuoxaUSX0GJSObvGA=="
    crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13/l10n/ar-dz.min.js"
    integrity="sha512-qpDG6agspDXhnOZkCoWtFNJ13B6Fq6pwIuZoLw0b05J8TDd1qohuTaemmrpsN3ZVtB7AI7ZnqH5CVVIj01SV5g=="
    crossorigin="anonymous" referrerpolicy="no-referrer"></script>

%%add_js%%

<script>
    var currentButton = undefined;
    $(".btn-submit").on('click', function (event) {
        currentButton = $(this)
    });
    $("#%%model_name%%_form").validate({
        submitHandler: function (form) {
            var buttonText = currentButton.text();
            currentButton.prop("disabled", true).html("{{_('Please wait')}}");
            var formData = $('#%%model_name%%_form').serializeArray(); 
            var jsonData = {}; 
            formData.forEach(function(item) {jsonData[item.name] = item.value;}); 
            var type = currentButton.data('type');

            $.ajax({
                type: "POST",
                url: "/admin/%%route%%/save",
                data: JSON.stringify(jsonData),
                contentType: 'application/json;charset=utf-8', 
                processData: false,
                success: function (data) {
                    toastr.options.timeOut = 200;
                    toastr.options.onHidden = function () {
                        currentButton.prop("disabled", false).html(buttonText);
                        if (type == 'submit-return') {
                            window.location.href = '/admin/%%route%%';
                        } else if (type == 'submit-new-entry') {
                            window.location.href = '/admin/%%route%%/add';
                        } else {
                            window.location.reload();
                        }
                    };
                    toastr.success("{{_('Submit Successfully')}}");
                },
                error: function (xhr, status, error) {
                    let msg = xhr.responseJSON && xhr.responseJSON.msg ? xhr.responseJSON.msg : error;
                    toastr.error(msg);
                },
                complete: function (xhr, textStatus) {
                    $("#app-loading-indicator").addClass("opacity-0");
                    currentButton.prop("disabled", false).html(buttonText);
                },
            });

            return false;
        },
        errorElement: "div",
        errorPlacement: function (error, element) {
            $(element).removeClass('is-valid');
            $(element).addClass('is-invalid');
            error.addClass("mt-1 p-1 text-warning");
            if (element.prop("type") === "checkbox" || element.parent().find('button').length > 0) {
                error.insertAfter(element.parent());
            } else {
                error.insertAfter(element);
            }
        },
        success: function (label, element) {
            $(element).removeClass('is-invalid');
            $(element).addClass('is-valid mb-2');
            $(label).addClass('d-none');
        },
    });
</script>
{% endblock javascript %}
{% block content %}
<!-- Page body -->
<div class="page-body pt-6888">
    <div class="container-fluid px-4">
        <div class="row">
            <div class="col-md-5 mx-auto">
                <form id="%%model_name%%_form" method="post" action>
                    %%form_body%%
                    <div class="d-flex justify-content-between">
                        <button type="submit" form="%%model_name%%_form" data-type="submit"
                            class="btn btn-primary btn-submit">
                            {{_('Submit')}}
                        </button>
                        <button type="submit" form="%%model_name%%_form" data-type="submit-return"
                            class="btn btn-primary btn-submit">
                            {{_('Submit & Return')}}
                        </button>
                        <button type="submit" form="%%model_name%%_form" data-type="submit-new-entry"
                            class="btn btn-primary btn-submit">
                            {{_('Submit & New Entry')}}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>{% endblock content %}