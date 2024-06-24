

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


})();


$(document).ready(function () {
 
	$('.logout').click(function (e) {
		e.preventDefault();
		if (confirm('Are you sure you want to exit?')) {
			$.ajax({
				url: '/user/logout',
				type: 'POST',
				contentType: 'application/json',
				dataType: "json",
				beforeSend: function () {
					document.getElementById("app-loading-indicator").classList.remove("opacity-0");
				},
				success: function (response) {
					console.log(response)
					if (response.status == 1) {
						toastr.success(_('Logout Successfully'))
						setTimeout(function () {
							location.reload();
						}, 200);
					} else {
						var msg = response.msg;
						toastr.error(msg);
					}
				},
				error: function (response, status, error) {
					var response = JSON.parse(data);
					var msg = response.msg;
					toastr.error(msg);
				},
				complete: function () {
					document.getElementById("app-loading-indicator").classList.add("opacity-0");
				}
			});
		}
	});

	
});

//LOGIN
function LoginForm() {
	"use strict";
	$("#LoginFormButton").prop("disabled", true);
	$("#LoginFormButton").html("{{_('Please wait')}}");
	$("#app-loading-indicator").removeClass("opacity-0");

	var email = $("#email").val();
	if (email == "") {
		toastr.error(localize.missing_email);
		$("#LoginFormButton").prop("disabled", false);
		$("#LoginFormButton").html(localize.sign_in);
		$("#app-loading-indicator").addClass("opacity-0");
		return false;
	}
	var password = $("#password").val();
	if (password == "") {
		toastr.error(localize.missing_password);
		$("#LoginFormButton").prop("disabled", false);
		$("#LoginFormButton").html(localize.sign_in);
		$("#app-loading-indicator").addClass("opacity-0");
		return false;
	}

	var formData = new FormData();
	formData.append('email', $("#email").val());
	formData.append('password', $("#password").val());
	// Ajax Post
	$.ajax({
		type: "post",
		url: "/user/login",
		data: formData,
		contentType: false,
		processData: false,
		cache: false,
		dataType: "json",
		success: function (response) {
			console.log('success', response);
			$("#app-loading-indicator").addClass("opacity-0");
			localStorage.setItem('user_token', response.token);
			toastr.options.timeOut = 200;
			toastr.options.onHidden = function () {
				window.location.href = "/user/dashboard";
			}
			toastr.success(localize.login_redirect);
		},
		error: function (response) {
			console.log('error', response);
			toastr.error(response.responseJSON.msg);
			$("#LoginFormButton").prop("disabled", false);
			$("#LoginFormButton").html(localize.sign_in);
			$("#app-loading-indicator").addClass("opacity-0");
		}
	});
	return false;
}

//REGISTER
function RegisterForm() {
	"use strict";
	document.getElementById("RegisterFormButton").disabled = true;
	document.getElementById("RegisterFormButton").innerHTML = "{{_('Please wait')}}";
	document.querySelector('#app-loading-indicator')?.classList?.remove('opacity-0');
	var formData = new FormData();
	formData.append('name', $("#name_register").val());
	formData.append('surname', $("#surname_register").val());
	formData.append('password', $("#password_register").val());
	formData.append('password_confirmation', $("#password_confirmation_register").val());
	formData.append('email', $("#email_register").val());
	if ($('#affiliate_code').val() != 'undefined') {
		formData.append('affiliate_code', $("#affiliate_code").val());
	} else {
		formData.append('affiliate_code', null);
	}

	$.ajax({
		type: "post",
		url: "/user/register",
		data: formData,
		contentType: false,
		processData: false,
		success: function (data) {
			toastr.success(localize.register_redirect);
			setTimeout(function () {
				location.reload();
				document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
			}, 1500);
		},
		error: function (data) {
			var err = data.responseJSON.errors;
			var type = data.responseJSON.type;
			$.each(err, function (index, value) {
				toastr.error(value);
			});

			if (type === 'confirmation') {
				setTimeout(function () {
					location.href = '/login';
					document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
				}, 2500);
			} else {
				document.getElementById("RegisterFormButton").disabled = false;
				document.getElementById("RegisterFormButton").innerHTML = localize.signup;
				document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
			}
		}
	});
	return false;
}


//PASSWORD RESET
function PasswordResetMailForm() {
	"use strict";

	document.getElementById("PasswordResetFormButton").disabled = true;
	document.getElementById("PasswordResetFormButton").innerHTML = "{{_('Please wait')}}";
	document.querySelector('#app-loading-indicator')?.classList?.remove('opacity-0');

	var formData = new FormData();
	formData.append('email', $("#password_reset_email").val());

	$.ajax({
		type: "post",
		url: "/forgot-password",
		data: formData,
		contentType: false,
		processData: false,
		success: function (data) {
			toastr.success(localize.password_reset_link);
			document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
		},
		error: function (data) {
			var err = data.responseJSON.errors;
			$.each(err, function (index, value) {
				toastr.error(value);
			});
			document.getElementById("PasswordResetFormButton").disabled = false;
			document.getElementById("PasswordResetFormButton").innerHTML = "Send Instructions!";
			document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
		}
	});
	return false;
}

function PasswordReset(password_reset_code) {
	"use strict";

	document.getElementById("PasswordResetFormButton").disabled = true;
	document.getElementById("PasswordResetFormButton").innerHTML = "{{_('Please wait')}}";
	document.querySelector('#app-loading-indicator')?.classList?.remove('opacity-0');

	var formData = new FormData();
	formData.append('password', $("#password_register").val());
	formData.append('password_confirmation', $("#password_confirmation_register").val());
	formData.append('password_reset_code', password_reset_code);

	$.ajax({
		type: "post",
		url: "/forgot-password/save",
		data: formData,
		contentType: false,
		processData: false,
		success: function (data) {
			toastr.success(localize.password_reset_done);
			setTimeout(function () {
				location.href = '/dashboard';
				document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
			}, 1250);
		},
		error: function (data) {
			var err = data.responseJSON.errors;
			$.each(err, function (index, value) {
				toastr.error(value);
			});
			document.getElementById("PasswordResetFormButton").disabled = false;
			document.getElementById("PasswordResetFormButton").innerHTML = localize.password_reset;
			document.querySelector('#app-loading-indicator')?.classList?.add('opacity-0');
		}
	});
	return false;
}

