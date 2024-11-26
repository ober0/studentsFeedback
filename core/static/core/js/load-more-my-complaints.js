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
        fetch(`/loadmore/my/`, {
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
    const publishedStatus = complaint.is_published ?
        `<p style="color: lawngreen">✔ Опубликовано</p>` :
        `<p style="color: red">❌ Не опубликовано</p>`;
    const responseTextHtml = complaint.response_text ?
        `<p><strong>Ответ администратора: </strong>${responseText}</p>` :
        `<p><strong>Не просмотрено администрацией</strong></p>`;

    return `
        <div class="complaint" cid="${complaint.id}">
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">
                        ${isAnonymous ? "Анонимное обращение" : complaint.user_name}
                    </h5>
                    <h6 class="card-subtitle mb-2 text-muted">
                        <strong>Категория:</strong> ${complaint.category}
                    </h6>
                    <p class="card-text">
                        <strong>Текст обращения:</strong> ${complaint.content}
                    </p>
                    ${complaint.is_public ? publishedStatus : ""}
                    <hr>
                    ${responseTextHtml}
                    <p class="text-muted">Дата создания: ${complaint.created_at}</p>
                </div>
            </div>
        </div>
    `;
}


    // Загружаем контент при загрузке страницы
    loadMoreContent();

    // Добавляем обработчик для бесконечной прокрутки
    window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY + 350 >= document.body.offsetHeight) {
            loadMoreContent();
        }
    });
});
