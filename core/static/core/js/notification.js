document.addEventListener("DOMContentLoaded", () => {
    const toasts = document.querySelectorAll(".toast");
    toasts.forEach((toast, index) => {
        toast.style.top = `${index * 80}px`;

        toast.classList.add("active");
        const progress = toast.querySelector(".progress");

        progress.classList.add("active")

        setTimeout(() => {
            toast.classList.add("closing");
            setTimeout(() => {
                toast.remove();
            }, 500);и
        }, 5000);

        // Закрытие по нажатию на кнопку
        const closeIcon = toast.querySelector(".close");
        closeIcon.addEventListener("click", () => {
            toast.classList.add("closing");
            setTimeout(() => {
                toast.remove();
            }, 500);
        });
    });
});