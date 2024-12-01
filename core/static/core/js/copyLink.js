function resultCopy(result){
    if (result){
        let btn = document.getElementById('copy-link-btn')
        btn.innerText = 'Скопировано!'
        btn.disabled = true;
    }
    else {
        let parent = btn.parentNode

        btn.style.display = 'none'
        parent.querySelectorAll('.hidden').forEach(btn => {
            btn.classList.remove('hidden')
        })
    }
}

document.getElementById('copy-link-btn').addEventListener('click', function() {
    const linkText = document.getElementById('link-url').value;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(linkText)
            .then(() => {
                resultCopy(true)
            })
            .catch(err => {
                resultCopy(false)
            });
    }
    else {
        const tempInput = document.createElement('input');
        tempInput.value = linkText;
        document.body.appendChild(tempInput);
        tempInput.select();
        try {
            document.execCommand('copy');
            resultCopy(true)
        } catch (err) {
            resultCopy(false)
        }
        document.body.removeChild(tempInput);
    }
})