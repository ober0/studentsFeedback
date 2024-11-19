document.addEventListener("DOMContentLoaded", async function () {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;

    let formData = new FormData()
    formData.append('visitorId', visitorId)

    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch('/manage/complaint/load/', {
        method:'POST',
        headers:{
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
        .then(response => response.json())
        .then(result => {
            if (result.success){
                document.getElementById('complaint_id').value = result.id
                let data = `
                    <h2>Обращение #${result.id}</h2>
                    <h3>Категория ${result.category}</h3>
                    <p>Текст ${result.content}<p>
                    <p>Причина блокировки ${result.reason}</p>
                `
                const blocked_complaint = document.getElementById('blocked-complaint')
                blocked_complaint.innerHTML = data

                document.getElementById('form-block').innerHTML =
                `
                    <input type="hidden" name="device_identifier" value="${visitorId}">
                    <input type="text" placeholder="Письмо админстрации" name="text">
                    <input type="submit" value="Отправить">
                `
            }
            else {
                window.location.href = result.redirect
            }
        })
})