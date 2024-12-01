document.addEventListener("DOMContentLoaded", async function () {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;

    let formData = new FormData();
    formData.append('visitorId', visitorId);

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch('/manage/complaint/load/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById('complaint_id').value = result.id;

            // Формируем HTML с улучшёнными стилями
            let data = `
                <div class="card mb-4">
                    <div class="card-body">
                        
                        <h5 class="card-title">Обращение #${result.id}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">Категория: ${result.category}</h6>
                        <p class="card-text">Текст обращения: ${result.content}</p>
                        <hr>
                        <p class="card-text"><strong>Причина блокировки:</strong> ${result.reason}</p>
                        <p class="card-text"><strong>Конец блокировки:</strong> ${result.end}</p>
                    </div>
                </div>
            `;
            const blocked_complaint = document.getElementById('blocked-complaint');
            blocked_complaint.innerHTML = data;

            if (!result.isRequestSend) {
                document.getElementById('form-block').innerHTML = `
                    <input type="hidden" name="complaint_id" value="${result.id}">
                    <input type="hidden" name="device_identifier" value="${visitorId}">
                    <div class="form-group">
                        <textarea class="form-control mb-3" placeholder="Письмо администрации" name="text" rows="4"></textarea>
                    </div>
                    <input type="submit" class="btn btn-primary btn-block" value="Отправить запрос">
                `;
            }
            else {
                document.getElementById('form-block').innerHTML = `
                    <p>Обращение уже отправлено</p>
                    <p>Статус: ${result.status}</p>
                `;
            }

        } else {
            window.location.href = result.redirect;
        }
    });
});
