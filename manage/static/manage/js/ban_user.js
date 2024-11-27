document.getElementById('block_user').addEventListener('click', function () {
    let c_id = document.getElementById('id').value;
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    let reason = document.getElementById('reason').value;
    let time = document.getElementById('time').value;

    let formData = new FormData();
    formData.append('reason', reason);
    formData.append('time', time)
    fetch(`/manage/ban/${c_id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                window.location.href = '/manage/complaint/open/';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});
