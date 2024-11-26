document.addEventListener('DOMContentLoaded', function () {
    let isLoading = false;

    function loadMoreContent() {
        if (isLoading) return;

        isLoading = true;

        let complaintCount = document.querySelectorAll('.complaint').length;

        // Формируем данные для отправки
        const formData = new FormData();
        formData.append('start', Number(complaintCount));

        // Получаем CSRF токен
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        // Выполняем POST-запрос
        fetch(`loadmore/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    result.complaints.forEach((complaint) => {
                        const complaintHTML = createComplaint(complaint);
                        document.querySelector('.complaints').insertAdjacentHTML('beforeend', complaintHTML);
                    });
                } else {
                    console.error('Ошибка при загрузке жалоб:', result.error);
                }
            })
            .catch(error => {
                console.error('Ошибка запроса:', error);
            })
            .finally(() => {
                isLoading = false; // Сбрасываем флаг после завершения загрузки
            });
    }

    // Функция для создания HTML одной жалобы
    function createComplaint(complaint) {
        const isAnonymous = complaint.is_anonymous;
        const responseText = complaint.response_text || "Нет ответа";

        return `
            <div class="complaint" cid="${complaint.id}">
                <div class="card mb-4">
                    <div class="card-body">
                        <h5 class="card-title">
                            ${isAnonymous ? "Анонимное обращение" : complaint.user_name}
                        </h5>
                        <h6 class="card-subtitle mb-2 text-muted">
                            Категория: ${complaint.category}
                        </h6>
                        <p class="card-text">
                            Текст обращения: ${complaint.content}
                        </p>
                        <hr>
                        <p><strong>Ответ администратора:</strong> ${responseText}</p>
                        <p class="text-muted">
                            Дата создания: ${complaint.created_at}
                        </p>
                        <div id="${complaint.liked ? "unlike" : "like"}" class="like-btn">
                            <svg height="26" viewBox="0 0 24 24" width="26" xmlns="http://www.w3.org/2000/svg">
                                <g fill="none" fill-rule="evenodd">
                                    <path d="M0 0h24v24H0z"></path>
                                    <path 
                                        d="M16 4a5.95 5.95 0 0 0-3.89 1.7l-.12.11-.12-.11A5.96 5.96 0 0 0 7.73 4 5.73 5.73 0 0 0 2 9.72c0 3.08 1.13 4.55 6.18 8.54l2.69 2.1c.66.52 1.6.52 2.26 0l2.36-1.84.94-.74c4.53-3.64 5.57-5.1 5.57-8.06A5.73 5.73 0 0 0 16.27 4z"
                                        class="like-svg ${complaint.liked ? "like-press" : "like-no-press"}"></path>
                                </g>
                            </svg>
                            <span style="user-select: none" id="counter-${complaint.id}">
                                ${complaint.like_count}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Загружаем контент при загрузке страницы
    loadMoreContent();

    // Добавляем обработчик для бесконечной прокрутки
    window.addEventListener('scroll', () => {
        let footerHeight = document.getElementById('footer').offsetHeight + 50
        if (window.innerHeight + window.scrollY + footerHeight >= document.body.offsetHeight) {
            loadMoreContent();
        }
    });
});
