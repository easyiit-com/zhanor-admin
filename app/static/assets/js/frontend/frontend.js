
$(document).ready(() => {
    const token = localStorage.getItem("user_token");
    if (token === '') {
        token = 'default';
    }
    $.ajaxSetup({
        headers: {
            'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content'),
            'Authorization': 'Bearer ' + token
        }
    });
});
