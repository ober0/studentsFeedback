document.addEventListener('DOMContentLoaded', function () {
    const inputs = document.querySelectorAll('.input100');

    inputs.forEach(input => {
        if (input.value.trim() !== "") {
            input.classList.add('has-val');
        }

        input.addEventListener('input', function () {
            if (this.value.trim() !== "") {
                this.classList.add('has-val');
            } else {
                this.classList.remove('has-val');
            }
        });
    });
});