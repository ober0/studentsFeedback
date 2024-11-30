document.getElementById('remove_complaint').addEventListener('click', function () {
    let c_id = document.getElementById('id').value
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(`/complaints/delete/${c_id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                let next = document.getElementById('next').value
                if (next){
                    window.location.href = next;
                }
                else {
                    window.location.href = '/manage/complaint/open/';
                }
            }
        })
})