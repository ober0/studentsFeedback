document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('anonymous').addEventListener('change', function() {
        const name_groupField = document.querySelector('.name-group');
        if (this.checked) {
            name_groupField.classList.add('hidden');
            name_groupField.disabled = true;
        } else {
            name_groupField.classList.remove('hidden');
            name_groupField.disabled = false;
        }
    });

    document.querySelectorAll('input[name="response-method"]').forEach(function (radioButton) {
        radioButton.addEventListener('change', function () {
            const emailField = document.getElementById('email-field');
            const linkValue = document.querySelector('.link');

            // Проверяем существование элементов перед изменением классов
            if (!emailField || !linkValue) {
                console.error("Email field or link value element is missing.");
                return;
            }

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


    // Функция для установки или сброса ошибки
function errorField(field, reset = false) {
    if (reset) {
        field.style.borderColor = '';
    } else {
        field.style.borderColor = 'red';
    }

}

document.getElementById('submit-btn').addEventListener('click', async function () {
    let error = 0
    const form = document.getElementById('feedback-form');

    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;
    document.getElementById('pskey').value = visitorId;


    document.querySelectorAll('#feedback-form input, #feedback-form select, #feedback-form textarea').forEach(field => {
        errorField(field, true);
    });


    let selectCategoryField = document.getElementById('category');
    let selectCategoryValue = selectCategoryField.value;

    let nameField = document.getElementById('name');
    let nameValue = nameField.value;

    let groupField = document.getElementById('group');
    let groupValue = groupField.value;

    let isAnonymous = document.getElementById('anonymous').checked;

    let textField = document.getElementById('text');
    let textValue = textField.value;

    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    let emailField = document.getElementById('email');
    let emailValue = emailField.value;

    let responseTypeValue = form.elements['response-method'].value;


    if (!selectCategoryValue) {
        errorField(selectCategoryField);
        error++
    }

    if (!isAnonymous) {
        if (nameValue.length < 1) {
            errorField(nameField);
            error++
        }
        if (groupValue.length < 1) {
            errorField(groupField);
            error++
        }
    }

    if (textValue.length < 10) {
        errorField(textField);
        error++
    }

    if (responseTypeValue === 'email') {
        if (!emailPattern.test(emailValue)) {
            errorField(emailField);
            error++
        }
    }

    if (error === 0){
        form.submit();
    }

});

})