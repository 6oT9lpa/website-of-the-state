document.addEventListener('DOMContentLoaded', function() {
    const rejectedButton = document.getElementById('rejectedButton');
    const rejectReason = document.getElementById('rejectReason');
    const reasonInput = document.querySelector('.input-field');
    const formControl = document.getElementById('form-container');

    rejectedButton.addEventListener('click', function(event) {
        if (!reasonInput.value.trim()) {
            event.preventDefault();
            if (rejectReason.classList.contains('visible-input')) {
                rejectReason.classList.remove('visible-input');
                rejectReason.addEventListener('transitionend', function handleTransitionEnd() {
                    rejectReason.style.display = 'none';
                    rejectReason.removeEventListener('transitionend', handleTransitionEnd);
                }, { once: true });
            } else {
                rejectReason.style.display = 'flex';
                requestAnimationFrame(() => {
                    rejectReason.classList.add('visible-input');
                });
            }
        } 
        else {

            const formData = new FormData(formControl);
            formData.append('reason', reasonInput.value.trim());

            fetch('/resolution?uid={{ uid }}', {
                method: 'POST',
                body: formData,
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        }
    });
});        