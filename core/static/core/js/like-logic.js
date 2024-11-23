 function like(btn) {
        let cid = btn.closest('[cid]').getAttribute('cid');  // Получаем cid, используем closest для нахождения родителя

        let formData = new FormData();
        formData.append('cid', cid);  // Отправляем id жалобы

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

                let like = btn.querySelector('.like-svg')
                like.classList.remove('like-no-press')
                like.classList.add('like-press')
            } else {
                if (result.error === 'NotAuth') {
                    window.location.href = '/auth/?next=/';
                }
            }
        });
    }


    function unlike(btn) {
        let cid = btn.closest('[cid]').getAttribute('cid');

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

                let like = btn.querySelector('.like-svg')
                like.classList.add('like-no-press')
                like.classList.remove('like-press')
            } else {
                if (result.error === 'NotAuth') {
                    window.location.href = '/auth/?next=/';
                }
            }
        });
    }


    document.addEventListener('DOMContentLoaded', () => {
        document.body.addEventListener('click', function(event) {
            // Получаем кнопку с классом like-btn
            let btn = event.target.closest('.like-btn');
            
            if (btn) {
                if (btn.id === 'like') {
                    like(btn);
                }
                else if (btn.id === 'unlike') {
                    unlike(btn);
                }
            }
        });
    });