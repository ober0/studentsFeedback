document.addEventListener('DOMContentLoaded', function () {
    // Логика обработки изменения фильтра
document.querySelector('.select-filter').addEventListener('change', function () {
    const input = document.getElementById('search');
    const searchQuery = input.value;


    const selectElement = document.querySelector('.select-filter');
    const selectedValue = selectElement.value;
    if (selectedValue) {
        if (searchQuery) {
            window.location.href = `/board/?search=${searchQuery}&filter=${selectedValue}`;
        } else {
            window.location.href = `/board/?filter=${selectedValue}`;
        }
    } else {
        if (searchQuery) {
            window.location.href = `/board/?search=${searchQuery}`;
        } else {
            window.location.href = '/board/';
        }
    }
})

// Логика обработки нажатия Enter в поиске
document.getElementById('search').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const input = event.target;
        const searchQuery = input.value;

        const filterElement = document.querySelector('input[name="filter"]:checked');
        if (filterElement) {
            const filter = filterElement.value;
            if (searchQuery) {
                window.location.href = `/board/?search=${searchQuery}&filter=${filter}`;
            } else {
                window.location.href = `/board/?filter=${filter}`;
            }
        } else {
            if (searchQuery) {
                window.location.href = `/board/?search=${searchQuery}`;
            } else {
                window.location.href = '/board/';
            }
        }
    }
});

document.getElementById('search-go').addEventListener('click', function (){
    const input = this.parentElement.parentElement.querySelector('#search')
        const searchQuery = input.value;

        const filterElement = document.querySelector('input[name="filter"]:checked');
        if (filterElement) {
            const filter = filterElement.value;
            if (searchQuery) {
                window.location.href = `/board/?search=${searchQuery}&filter=${filter}`;
            } else {
                window.location.href = `/board/?filter=${filter}`;
            }
        } else {
            if (searchQuery) {
                window.location.href = `/board/?search=${searchQuery}`;
            } else {
                window.location.href = '/board/';
            }
        }
})

})