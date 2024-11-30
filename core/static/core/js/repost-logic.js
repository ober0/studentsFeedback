function repost(src) {
    const content = document.querySelector('content');
    const shareMenu = document.querySelector('.repost-open');

    // Затемняем основной контент
    if (content) {
        content.style.opacity = '0.1';
        content.classList.add('no-scroll');
    }

    // Отображаем меню
    if (shareMenu) {
        shareMenu.style.display = 'block';
        shareMenu.style.opacity = '1';
        shareMenu.querySelectorAll('button').forEach(btn => {
            btn.setAttribute('data-url', src);
        });
    }
}

function resultCopy(status, btn){
    if (status){
        btn.innerText = 'Скопировано!';
        btn.disabled = true;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    let isShareMenuOpened = false;

    document.body.addEventListener('click', function(event) {
        let btn = event.target.closest('.repost-btn');

        if (btn) {
            let link = btn.getAttribute('link');

            if (btn.id === 'copy') {
                link = btn.getAttribute('data-url');
                console.log(link)
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(link)
                        .then(() => resultCopy(true, btn))
                        .catch(err => resultCopy(false, btn));
                } else {
                    const tempInput = document.createElement('input');
                    tempInput.value = link;
                    document.body.appendChild(tempInput);
                    tempInput.select();
                    try {
                        document.execCommand('copy');
                        resultCopy(true, btn);
                    } catch (err) {
                        resultCopy(false, btn);
                    }
                    document.body.removeChild(tempInput);
                }


            } else {
                repost(link);
                isShareMenuOpened = true;
            }
        }
    });


    const closeButton = document.querySelector('.btn-close');

    // Закрытие окна при клике на крестик
    closeButton.addEventListener('click', () => {
        hiderepost()
    });




    document.addEventListener('keydown', function (event) {
        if (isShareMenuOpened){
            if (event.key === 'Escape'){
                hiderepost()
            }
        }
    })

});

function hiderepost() {
    // Сбрасываем стиль `content`
    const content = document.querySelector('content');
    if (content) {
        content.style.opacity = '1';
        content.classList.remove('no-scroll');
    }

    // Скрываем меню
    const shareMenu = document.querySelector('.repost-open');
    if (shareMenu) {
        shareMenu.style.display = 'none';
        shareMenu.style.opacity = '0';
    }
}



