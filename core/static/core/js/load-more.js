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
                        if (Number(result.complaints_count) <= document.querySelectorAll('.complaint').length){
                            window.removeEventListener('scroll', loadMore);
                        }
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
                        <div class="buttons">
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
                            
                            <div class="repost-btn" link="${complaint.link}">
                                 <svg height="26" viewBox="0 0 24 24" width="26" xmlns="http://www.w3.org/2000/svg">
                                     <g fill="none" fill-rule="evenodd">
                                         <path d="M0 0h24v24H0z"></path>
                                         <path d="M12 3.73c-1.12.07-2 1-2 2.14v2.12h-.02a9.9 9.9 0 0 0-7.83 10.72.9.9 0 0 0 1.61.46l.19-.24a9.08 9.08 0 0 1 5.84-3.26l.2-.03.01 2.5a2.15 2.15 0 0 0 3.48 1.69l7.82-6.14a2.15 2.15 0 0 0 0-3.38l-7.82-6.13c-.38-.3-.85-.46-1.33-.46zm.15 1.79c.08 0 .15.03.22.07l7.82 6.14a.35.35 0 0 1 0 .55l-7.82 6.13a.35.35 0 0 1-.57-.28V14.7a.9.9 0 0 0-.92-.9h-.23l-.34.02c-2.28.14-4.4.98-6.12 2.36l-.17.15.02-.14a8.1 8.1 0 0 1 6.97-6.53.9.9 0 0 0 .79-.9V5.87c0-.2.16-.35.35-.35z" fill="currentColor" fill-rule="nonzero"></path>
                                     </g>
                                 </svg>
                                 <span style="user-select: none">
                                    Поделиться
                                 </span>
                            </div>
                        </div>
                        
                </div>
            </div>
        `;
    }

    // Загружаем контент при загрузке страницы
    loadMoreContent();


    function loadMore() {
        let footerHeight = document.getElementById('footer').offsetHeight + 50
        if (window.innerHeight + window.scrollY + footerHeight >= document.body.offsetHeight) {
            loadMoreContent();
        }
    }
    // Добавляем обработчик для бесконечной прокрутки
    window.addEventListener('scroll', loadMore);


});
