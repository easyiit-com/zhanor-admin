
$(document).ready(function () {
	$('.upload').each(function () {
		var uploadElement = $(this);
		var hiddenInput = uploadElement.siblings('input[type="hidden"]');
		var imagesContainer = uploadElement.siblings('.images-container');
		var uploadType = uploadElement.data('upload-type');
		var initialValues = hiddenInput.val() ? hiddenInput.val().split(',') : [];
		$.each(initialValues, function (i, imageUrl) {
			var trimmedImageUrl = imageUrl.trim();
			if (uploadType === 'file' && trimmedImageUrl) {
				trimmedImageUrl = '/static/assets/images/file.png';
			}
			if (trimmedImageUrl) {
				createFileDiv(imagesContainer, trimmedImageUrl, hiddenInput, imageUrl.trim());
			}
		});
	});
	$(document).on('change', '.upload', function (e) {
		const fileInput = $(this);
		let allowedExtensionsStr = fileInput.data('allowed-extensions');
		const uploadType = fileInput.data('upload-type');
		const imagesContainer = fileInput.siblings('.images-container');
		const hiddenInput = fileInput.siblings('input[type="hidden"]');
		var save = fileInput.data('save');
		var replace = false
		if (!fileInput[0].multiple){
			replace = true;
            imagesContainer.html('');
            hiddenInput.val('');
		}
		if (typeof allowedExtensionsStr !== 'string') {
			allowedExtensionsStr = ".jpg,.jpeg,.png,.gif";
		}
		const allowedExtensions = allowedExtensionsStr.split(',');
		const validFiles = [];

		$.each(fileInput[0].files, function (i, file) {
			const fileName = file.name;
			const fileExtension = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase();
			if (allowedExtensions.includes('.' + fileExtension)) {
				validFiles.push(file); 
			} else {
				toastr.error(_(`File "${fileName}" is not an allowed format (only ${allowedExtensions.join(', ')} are allowed), and this file has been skipped.`));
			}
		});

		if (validFiles.length > 0) {
			uploadFile(validFiles, hiddenInput, uploadType, save, imagesContainer);
			fileInput.val('');
		}
	});

	function uploadFile(files, hiddenInput, uploadType, save = 'true', imagesContainer) {
		const fileData = new FormData();
		fileData.append("save", save); 
		$.each(files, function (i, file) {
			fileData.append("files[]", file);
		});

		$.ajax({
			url: '/upload',
			type: 'POST',
			processData: false,
			contentType: false,
			data: fileData,
			success: function (data) {
				if (data.code === 200) {
					$.each(data.data, function (i, fileInfo) {
						const currentVal = hiddenInput.val();
						const newVal = currentVal ? (currentVal + ',' + fileInfo.relative_url) : fileInfo.relative_url;
						hiddenInput.val(newVal);
						createFileDiv(imagesContainer, fileInfo.relative_url, hiddenInput, fileInfo.relative_url, uploadType);
					});
					toastr.success(_('Upload Successfully'))
				}
			},
			error: function (xhr, status, error) {
				toastr.error(_("Failed to upload files."));
			}
		});
	}
	function createFileDiv(imagesContainer, displayUrl, hiddenInput, originalUrl, uploadType) {
		var imgDiv = ''
		var extension = originalUrl.substring(originalUrl.lastIndexOf('.') + 1);
		if (uploadType == "file") {
			imgDiv = $('<div class="col-6 col-sm-3"><label class="form-image m-2"><i class="ti ti-x delete-image-btn" data-url="' + originalUrl + '"></i><img src="/static/assets/images/file-type-' + extension + '.png" class="form-image-image" onError="/static/assets/images/file.png"></label></div>');
		} else {
			imgDiv = $('<div class="col-6 col-sm-3"><label class="form-image m-2"><i class="ti ti-x delete-image-btn" data-url="' + originalUrl + '"></i><img src="' + displayUrl + '" class="form-image-image" onError="/static/assets/images/file.png"></label></div>');
		}
		imagesContainer.append(imgDiv);
		imgDiv.find('.delete-image-btn').on('click', function () {
			var containerDiv = $(this).closest('div.col-6.col-sm-3');
			var urls = hiddenInput.val().split(',');
			var filteredUrls = urls.filter(function (url) { return url !== $(this).data('url'); }.bind(this));
			hiddenInput.val(filteredUrls.join(','));
			containerDiv.remove();
		});
	}
});
