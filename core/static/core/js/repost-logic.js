function repost(src) {
    const main = document.querySelector('main');
    const header = document.querySelector('header');
    const footer = document.querySelector('footer');
    const shareMenu = document.querySelector('.repost-open');

    // Затемняем основной контент
    if (main) {
        main.style.opacity = '0.1';
        main.classList.add('no-scroll');
    }

    if (header) {
        header.style.opacity = '0.1';
        header.classList.add('no-scroll');
    }

    if (footer) {
        footer.style.opacity = '0.1';
        footer.classList.add('no-scroll');
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
   const main = document.querySelector('main');
    const header = document.querySelector('header');
    const footer = document.querySelector('footer');

    // Затемняем основной контент
    if (main) {
        main.style.opacity = '1';
        main.classList.remove('no-scroll');
    }

    if (header) {
        header.style.opacity = '1';
        header.classList.remove('no-scroll');
    }

    if (footer) {
        footer.style.opacity = '1';
        footer.classList.remove('no-scroll');
    }

    // Скрываем меню
    const shareMenu = document.querySelector('.repost-open');
    if (shareMenu) {
        shareMenu.style.display = 'none';
        shareMenu.style.opacity = '0';
    }
}



