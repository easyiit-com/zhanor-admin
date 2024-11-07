// general_config.js

$(document).ready(function () {
	"general_config strict";
	var clipboard = new ClipboardJS('.copy');

	clipboard.on('success', function (e) {
		e.trigger.classList.add('copied'); // 添加一个表示已复制的类
		setTimeout(function () {
			e.trigger.classList.remove('copied'); // 延迟一段时间后移除该类，以便下次点击时重新显示动画
		}, 1000); // 根据需要调整延迟时间

		// 显示打勾动画
		var checkmark = e.trigger.querySelector('.checkmark');
		// checkmark.display = 'block'; 
		toastr.success(_('Copy Successfully'))
	});

	clipboard.on('error', function (e) {
		console.error(_('Copy Failed'));
	});


	$(document).on('click', '.delete', function (e) {
		const row = $(this).data('row');
		$('#' + row).remove()
	})


	$(document).on('click', '.btn-index-add', function (e) {
		var key = $(this).data('key');
		var name = $(this).data('name');

		var templateRow = `
		<div class="row g-2 p-2" id="row-basic-${name}-${key}">
			<div class="col-4">
				<input class="form-control" type="text" name="row[${name}][${key}][key]" value="">
			</div>
			<div class="col-4">
				<input class="form-control" type="text" name="row[${name}][${key}][value]" value="" placeholder="">
			</div>
			<div class="col-4 d-inline-block align-middle p-2 align-items-center">
				<a href="javascript:;" class="btn btn-danger btn-icon delete" aria-label="Delete" data-row="row-basic-${name}-${key}">
					<!-- Download SVG icon from http://tabler-icons.io/i/brand-facebook -->
					<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-x" width="24" height="24" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
						<path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
						<path d="M18 6l-12 12"></path>
						<path d="M6 6l12 12"></path>
					</svg>
				</a>

				<a href="javascript:;" class="btn btn-icon" aria-label="Move">
					<!-- Download SVG icon from http://tabler-icons.io/i/brand-facebook -->
					<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-arrows-move" width="24" height="24" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
						<path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
						<path d="M18 9l3 3l-3 3"></path>
						<path d="M15 12h6"></path>
						<path d="M6 9l-3 3l3 3"></path>
						<path d="M3 12h6"></path>
						<path d="M9 18l3 3l3 -3"></path>
						<path d="M12 15v6"></path>
						<path d="M15 6l-3 -3l-3 3"></path>
						<path d="M12 3v6"></path>
					</svg>
				</a>
			</div>
		</div>
		`;
		templateRow = $(templateRow); // 将HTML字符串转化为jQuery对象
		templateRow.insertBefore($(this));
		key++;
		$(this).data('key', key);
	});

	$(document).on('click', '.btn-add', function (e) {
		var key = $(this).data('key');
		var templateRow = `
		<div class="row g-2 p-2" id="row-basic-${key}">
			<div class="col-4">
				<input class="form-control arrays" type="text" name="row[${key}][key]" value="">
			</div>
			<div class="col-4">
				<input class="form-control arrays" type="text" name="row[${key}][value]" value="" placeholder="">
			</div>
			<div class="col-4 d-inline-block align-middle p-2 align-items-center">
				<a href="javascript:;" class="btn btn-danger btn-icon delete" aria-label="Delete" data-row="row-basic-${key}">
					<!-- Download SVG icon from http://tabler-icons.io/i/brand-facebook -->
					<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-x" width="24" height="24" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
						<path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
						<path d="M18 6l-12 12"></path>
						<path d="M6 6l12 12"></path>
					</svg>
				</a>

				<a href="javascript:;" class="btn btn-icon" aria-label="Move">
					<!-- Download SVG icon from http://tabler-icons.io/i/brand-facebook -->
					<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-arrows-move" width="24" height="24" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
						<path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
						<path d="M18 9l3 3l-3 3"></path>
						<path d="M15 12h6"></path>
						<path d="M6 9l-3 3l3 3"></path>
						<path d="M3 12h6"></path>
						<path d="M9 18l3 3l3 -3"></path>
						<path d="M12 15v6"></path>
						<path d="M15 6l-3 -3l-3 3"></path>
						<path d="M12 3v6"></path>
					</svg>
				</a>
			</div>
		</div>
		`;
		templateRow = $(templateRow); // 将HTML字符串转化为jQuery对象
		templateRow.insertBefore($(this));
		key++;
		$(this).data('key', key);
	});
	let optionsData = {};
	$(document).on('input', '.arrays', function () {
		const keyInput = $(this);
		const parts = keyInput.attr('name').split('[');
		// 获取索引和字段类型
		const indexStr = parts[1].slice(0, -1);
		const index = parseInt(indexStr);
		const fieldType = parts[2].slice(0, -1);

		if (fieldType === 'key') {
			optionsData[index] = { key: keyInput.val() };
		} else if (fieldType === 'value' && optionsData[index]) {
			optionsData[index].value = keyInput.val();
			updateOptionsValue();
		}

		function updateOptionsValue() {
			const transformedData = Object.entries(optionsData)
				.filter(item => item[1].key && item[1].value)
				.reduce((acc, [_, v]) => ({ ...acc, [v.key]: v.value }), {});

			$('input[name=value]').val(JSON.stringify(transformedData));
		}
	});




	$(document).on("change", "#congfig-type", function () {
		var value = $(this).val();
		$(".tf").addClass("hidden");
		$(".tf.tf-" + value).removeClass("hidden");
		console.log(value, ["selectpage", "selectpages"].indexOf(value) > -1);

		if (["selectpage", "selectpages"].indexOf(value) > -1) {
			console.log('ajxa');
			//异步加载表列表
			$.ajax({
				url: "/admin/general/config/table/list",
				type: "post",
				contentType: 'application/x-www-form-urlencoded',
				processData: false,
				success: function (data) {
					console.log('ajxa', data.data);
					var $selectElement = $("#c-selectpage-table");
					$selectElement.empty();
					$.each(data.data, function (index, value) {
						console.log(value);
						var $option = $("<option>", {
							value: value,
							text: value
						});
						$selectElement.append($option);
					});
				}
			})
		}
	});


	$(document).on('click', '#rule-dropdown-menu a.dropdown-item', function (e) {
		e.preventDefault(); // 阻止默认的链接行为

		var $ruleInput = $('input[name="rule"]'); // 获取name为"rule"的输入元素
		var currentValue = $ruleInput.val(); // 获取当前值
		var newValue = $(this).data('value'); // 获取点击a标签的data-value属性值

		// 检查新值是否已经存在于现有值中
		if (currentValue.includes(newValue)) {
			return; // 如果已存在，则不执行任何操作
		} else {
			// 新值不存在于现有值中，则添加到现有值后面并以英文逗号分隔
			$ruleInput.val(currentValue ? currentValue + ',' + newValue : newValue);
		}
	});

});



function GeneralConfigSave() {
	"general_config strict";
	document.getElementById("general_config_button").disabled = true;
	document.getElementById("general_config_button").innerHTML = "Please wait";
	document.getElementById("app-loading-indicator").classList.remove("opacity-0");
	var formData = $('#general_config_form').serializeArray(); 
    var jsonData = {}; 
    formData.forEach(function(item) {jsonData[item.name] = item.value;}); 
	$.ajax({
		type: "post",
		url: "/admin/general/config/save",
		data: JSON.stringify(jsonData),
        contentType: 'application/json;charset=utf-8', 
        processData: false,
		success: function (data) {
			toastr.success(_('Submit Successfully'))
			document.getElementById("general_config_button").disabled = false;
			document.getElementById("general_config_button").innerHTML = "Submit";
		},
		error: function (data) {
			var msg = data.responseJSON.msg;
			toastr.error(msg);
			document.getElementById("general_config_button").disabled = false;
			document.getElementById("general_config_button").innerHTML = "Submit";
		},
		complete: function (xhr, textStatus) {
			document.getElementById("app-loading-indicator").classList.add("opacity-0");
		},

	});
	return false;
}

function GeneralConfigDelete(GeneralConfigId) {
	if (confirm(_('Are you sure you want to delete it?'))) {
		$.ajax({
			type: "DELETE",
			url: "/admin/general/config/delete",
			data: JSON.stringify({ id: GeneralConfigId }),
            contentType: 'application/json;charset=utf-8', 
            processData: false,
			success: function (data) {
				const general_configElement = document.getElementById('general_config-' + GeneralConfigId);
				if (general_configElement) {
					general_configElement.remove();
				}
				toastr.success(localize.delete_done)
			},
			error: function (data) {
				var msg = data.responseJSON.msg;
				toastr.error(msg);
			}
		});
	}
	return false;
}

