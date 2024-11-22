function like(btn) {
    let cid = btn.parentElement.parentElement.parentElement.parentElement.getAttribute('cid')

    let formData = new FormData();
    formData.append('cid', cid);

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch('/complaints/like/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                let like_counter = document.getElementById(`counter-${cid}`);
                if (like_counter) {
                    let like_count = Number(like_counter.innerText);
                    let new_like_count = like_count + 1;
                    like_counter.innerText = new_like_count;
                }

                btn.id = 'unlike';
                btn.classList.remove('like-no-press')
                btn.classList.add('like-press')
            } else {
                if (result.error === 'NotAuth') {
                    window.location.href = '/auth/?next=/';
                }
            }
        });
}

function unlike(btn) {
    let cid = btn.parentElement.parentElement.parentElement.parentElement.getAttribute('cid')

    let formData = new FormData();
    formData.append('cid', cid);

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch('/complaints/unlike/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                let like_counter = document.getElementById(`counter-${cid}`);
                if (like_counter) {
                    let like_count = Number(like_counter.innerText);
                    let new_like_count = like_count - 1;
                    like_counter.innerText = new_like_count;
                }

                btn.id = 'like';
                btn.classList.add('like-no-press')
                btn.classList.remove('like-press')
            } else {
                if (result.error === 'NotAuth') {
                    window.location.href = '/auth/?next=/';
                }
            }
        });
}



document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'like') {
            like(event.target);
        }
        else if (event.target && event.target.id == 'unlike'){
            unlike(event.target)
        }

    });
});
