document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('anonymous').addEventListener('change', function() {
        const nameField = document.querySelector('.name_place');
        const groupField = document.querySelector('.group_place');
        if (this.checked) {
            nameField.classList.add('hidden');
            groupField.classList.add('hidden');
            nameField.disabled = true;
            groupField.disabled = true;
        } else {
            nameField.classList.remove('hidden');
            groupField.classList.remove('hidden');
            nameField.disabled = false;
            groupField.disabled = false;
        }
    });

    document.querySelectorAll('input[name="response-method"]').forEach(function(radioButton) {
        radioButton.addEventListener('change', function() {
            const emailField = document.getElementById('email-field');
            const linkValue = document.querySelector('.link');
            if (document.getElementById('response-email').checked) {
                emailField.classList.remove('hidden');
                linkValue.classList.add('hidden');
                document.getElementById('email').required = true;
            } else {
                emailField.classList.add('hidden');
                linkValue.classList.remove('hidden');
                document.getElementById('email').required = false;
            }
        });
    });

    // Обработчик отправки формы
    document.getElementById('submit-btn').addEventListener('click', async function () {
        const form = document.getElementById('feedback-form');
        console.log(form)
        // Загружаем FingerprintJS
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        const visitorId = result.visitorId;

        // Устанавливаем значение в скрытое поле
        document.getElementById('pskey').value = visitorId;

        // Отправляем форму
        form.submit()
    });

})