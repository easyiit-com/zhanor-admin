$(document).ready(function () {
    "use strict";

    // 初始化编辑器的函数
    function initAceEditor(elementId, mode) {
        var editor = ace.edit(elementId);
        editor.session.setMode("ace/mode/" + mode);
        editor.setTheme("ace/theme/dracula");
        return editor;
    }

    var editors = {
        model: initAceEditor("model_code", "python"),
        template_index: initAceEditor('template_index_code', 'html'),
        template_add: initAceEditor('template_add_code', 'html'),
        template_edit: initAceEditor('template_edit_code', 'html'),
        views: initAceEditor('views_code', 'python'),
        api: initAceEditor('api_code', 'python'),
        schema: initAceEditor('schema_code', 'python'),
        js: initAceEditor('js_code', 'javascript'),
        route: initAceEditor('route_code', 'python')
    };

    $("body").on("change", ".table_name", function () {
        const tableName = $(this).val();
        fetchTableFields(tableName);
    });

    function fetchTableFields(tableName) {
		var formData = new FormData();
		formData.append('table_name', tableName);
        $.ajax({
            type: "post",
            url: "/admin/generator/code",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                updateCheckboxes(data.data.table_fields);
                showCode(data.data);
            },
            error: handleError
        });
    }

    function updateCheckboxes(tableFields) {
        var checkboxesHtml = tableFields.map(field => `
            <label class="form-check form-check-inline">
                <input class="form-check-input table_fields" type="checkbox" name="fields[]" value="${field}" checked>
                <span class="form-check-label">${field}</span>
            </label>
        `).join("");

        $('#table_fields').html(checkboxesHtml);
        $('#table_fields').on('click', '.table_fields', updateCode);
        $('#controllers').on('click', '.controller', updateCode);
    }

    function updateCode() {
        const tableName = $('#table_name').val();
        const checkedFieldsValues = $('.table_fields:checked').map(function () { return this.value; }).get().join(",");
        const checkedControllerValues = $('.controller:checked').map(function () { return this.value; }).get().join(",");

        var formData = new FormData();
        formData.append('table_name', tableName);
        formData.append('fields', checkedFieldsValues);
        formData.append('controllers', checkedControllerValues);

        $.ajax({
            type: "post",
            url: "/admin/generator/code",
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                showCode(data.data);
                toastr.success('Get Successfully');
            }
        });
    }

    function showCode(data) {
        Object.keys(editors).forEach(key => {
			console.log(key + '_code')
            editors[key].setValue(data[key + '_code']);
        });
    }

    function handleError(data) {
        var errors = data.responseJSON.errors;
        $.each(errors, function (index, value) {
            toastr.error(value);
        });
		console.log("Some Errors")
        toggleGeneratorButton(false, "Save");
    }

    function toggleGeneratorButton(disabled, text) {
        document.getElementById("generator_button").disabled = disabled;
        document.getElementById("generator_button").innerHTML = text;
    }

    function generator() {
        toggleGeneratorButton(true, "{{_('Please wait')}}");

        var formData = new FormData();
        formData.append('table_name', $("#table_name").val());

        ['model', 'template_index', 'template_add', 'template_edit', 'views', 'api', 'schema', 'js'].forEach(type => {
            formData.append(`${type}_code_checked`, $(`#${type}_code_checked`).is(':checked') ? 1 : 0);
            formData.append(`${type}_code`, editors[type].getValue());
        });

        formData.append("generate_menu_checked", $("#generate_menu_checked").is(':checked') ? 1 : 0);

        $.ajax({
            type: "post",
            url: "/admin/generator/create_file",
            data: formData,
            contentType: false,
            processData: false,
            success: function () {
                toastr.success(_('Submit Successfully'));
                toggleGeneratorButton(false, "Submit");
            },
            error: function (data) {
                toastr.error(data.responseJSON.msg);
                toggleGeneratorButton(false, "Submit");
            }
        });
        return false;
    }

    // 绑定按钮点击事件
    $("#generator_button").click(function (event) {
        event.preventDefault();
        generator();
    });
});
