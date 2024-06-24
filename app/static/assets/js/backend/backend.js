
(() => {
	"use strict";
 
	const navbarExpander = document.querySelector('.navbar-expander');
	const dropdownMenus = document.querySelectorAll('.dropdown-menu');
	const frontendLocalNav = document.querySelector('#frontend-local-navbar');
	const siteHeader = document.querySelector('#site-header');
	function handleStickyHeader() {
		if (!siteHeader) return;
		if (window.scrollY >= siteHeaderOffsetTop) {
			siteHeader.classList.add('lqd-is-sticky');
			siteHeader.style.position = 'fixed';
			siteHeader.style.top = '0';
		} else {
			siteHeader.classList.remove('lqd-is-sticky');
			siteHeader.style.position = '';
			siteHeader.style.top = '';
		}
	}

	function onWindowScroll(ev) {
		handleStickyHeader();
	}

	function onWindowResize() {
		if (siteHeader) {
			siteHeader.classList.remove('lqd-is-sticky');
			siteHeader.style.position = '';
			siteHeader.style.top = '';
			siteHeaderOffsetTop = siteHeader?.offsetTop || 0;
		}
		handleStickyHeader();
	}

	 

	dropdownMenus.forEach(dd => {
		if (document.body.classList.contains('navbar-shrinked')) {
			dd.classList.remove('show');
		}
	}); 

	navbarExpander?.addEventListener('click', event => {
		event.preventDefault();
		const navbarIsShrinked = document.body.classList.contains('navbar-shrinked');
		document.body.classList.toggle('navbar-shrinked');
		localStorage.setItem('lqd-navbar-shrinked', !navbarIsShrinked);
	});

	document.addEventListener('click', ev => {
		const { target } = ev;
		dropdownMenus
			.forEach(dd => {
				if (!document.body.classList.contains('navbar-shrinked') && dd.closest('.primary-nav')) return;
				const clickedOutside = !dd.parentElement.contains(target);
				if (clickedOutside) {
					dd.classList.remove('show'); 
				};
			})
	});
  
	if (frontendLocalNav) {
		const scrollspy = VanillaScrollspy({ menu: frontendLocalNav })
		scrollspy.init()
	}
 
	window.addEventListener('scroll', onWindowScroll);

	window.addEventListener('resize', onWindowResize);


	$(document).ready(function () {
		$.ajaxSetup({
			headers: {
				'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
			}
		});
		$('.ajax').each(function () {
			var $this = $(this);
			var modelUrl = '/admin/' + $this.data('model').replace(/_/g, "/");
			var title = $this.data('title');
			var valueData = $this.data('value');

			var values;
			if ($this.is('select') && $this.prop('multiple')) {
				values = valueData.split(',');
			} else {
				values = [valueData.toString()];
			}
			$.ajax({
				url: modelUrl,
				method: 'GET',
				dataType: 'json',
				success: function (data) {
					if ($this.is('select')) {
						$.each(data.data, function (index, item) {
							var isSelected = values.includes(item.id.toString());
							var optionHtml = '<option value="' + item.id + '"' + (isSelected ? ' selected="selected"' : '') + '>' + item[title] + '</option>';
							$this.append(optionHtml);
						});
					} else {

					}
				},
				error: function (jqXHR, textStatus, errorThrown) {
					console.error('Ajax request fail', textStatus, ', Error', errorThrown);
				}
			});
		});

		
		
		$('.clear-cache').click(function (e) {
			e.preventDefault();
			if (confirm(_("Are you sure you want to clear the cache?"))) {
				$.ajax({
					url: '/admin/cache/clear/all',
					type: 'POST',
					beforeSend: function () {
						document.getElementById("app-loading-indicator").classList.remove("opacity-0");
					},
					success: function (data) {
						console.log(data)
						if (data.status == 1) {
							toastr.success('Clean Successfully')
						} else {
							toastr.error(data.msg);
						}
					},
					error: function (data, status, error) {
						toastr.error(data.msg);
					},
					complete: function () {
						document.getElementById("app-loading-indicator").classList.add("opacity-0");
					}
				});
			}
		});

		$('.logout').click(function (e) {
			e.preventDefault();
			if (confirm('Are you sure you want to exit?')) {
				$.ajax({
					url: '/admin/logout',
					type: 'POST',
					contentType: 'application/json',
					beforeSend: function () {
						document.getElementById("app-loading-indicator").classList.remove("opacity-0");
					},
					success: function (response) {
						toastr.options.timeOut = 200;
						toastr.options.onHidden = function () {
							window.location.reload();
						}
						toastr.success('Logout Successfully');
					},
					error: function (response, status, error) {
						let msg = response.responseJSON.msg;
						toastr.error(msg);
					},
					complete: function () {
						document.getElementById("app-loading-indicator").classList.add("opacity-0");
					}
				});
			}
		});
	});

})();
