async function sendFingerprint() {
    const fp = await FingerprintJS.load();
    const result = await fp.get();
    const visitorId = result.visitorId;

    fetch('/manage/check_fingerprint/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fingerprint: visitorId })
    })
        .then(response => response.json())
        .then(data => {
            if (data.isBlocked){
                window.location.href = '/blocked/'
            }
        })
}
sendFingerprint()