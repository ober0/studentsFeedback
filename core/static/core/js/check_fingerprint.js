async function sendFingerprint() {
    let visitorId_local_storage = localStorage.getItem('fingerprint')

    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;



    const formData = new FormData();
    if (visitorId_local_storage != visitorId){
        localStorage.setItem('fingerprint', visitorId)
        formData.append('old_fingerprint', visitorId_local_storage)
    }
    formData.append('fingerprint', visitorId);
    fetch('/manage/check_fingerprint/', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.isBlocked) {
                window.location.href = '/blocked/';
            }
        })
}
sendFingerprint();
