document.getElementById('search').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        const input = event.target;
        const searchQuery = input.value;


        if (searchQuery) {
            window.location.href = `/complaints/my/?search=${searchQuery}`;
        } else {
            window.location.href = '/complaints/my/';
        }
    }
});

document.getElementById('search-go').addEventListener('click', function (){
    const input = this.parentElement.parentElement.querySelector('#search')
    const searchQuery = input.value;

    if (searchQuery) {
        window.location.href = `/complaints/my/?search=${searchQuery}`;
    } else {
        window.location.href = '/complaints/my/';
    }
})