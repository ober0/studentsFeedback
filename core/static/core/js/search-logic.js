// Логика обработки изменения фильтра
document.querySelectorAll('input[name="filter"]').forEach(radio => {
    radio.addEventListener('change', function () {
        const input = document.getElementById('search');
        const searchQuery = input.value;

        const filterElement = document.querySelector('input[name="filter"]:checked');
        if (filterElement) {
            const filter = filterElement.value;
            if (searchQuery) {
                window.location.href = `/?search=${searchQuery}&filter=${filter}`;
            } else {
                window.location.href = `/?filter=${filter}`;
            }
        } else {
            if (searchQuery) {
                window.location.href = `/?search=${searchQuery}`;
            } else {
                window.location.href = '/';
            }
        }
    });
});

// Логика обработки нажатия Enter в поиске
document.getElementById('search').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const input = event.target;
        const searchQuery = input.value;

        const filterElement = document.querySelector('input[name="filter"]:checked');
        if (filterElement) {
            const filter = filterElement.value;
            if (searchQuery) {
                window.location.href = `/?search=${searchQuery}&filter=${filter}`;
            } else {
                window.location.href = `/?filter=${filter}`;
            }
        } else {
            if (searchQuery) {
                window.location.href = `/?search=${searchQuery}`;
            } else {
                window.location.href = '/';
            }
        }
    }
});
