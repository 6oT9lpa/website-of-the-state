document.addEventListener('DOMContentLoaded', () => {
    const accessMessage = document.querySelector('#access-message');

    if (accessMessage) {
        accessMessage.classList.add('hidden'); 

        setTimeout(() => {
            accessMessage.style.display = 'block';
            accessMessage.style.transform = 'translateY(30px)';

            setTimeout(() => {
                accessMessage.style.transform = 'translateY(0px)';
                accessMessage.classList.add('show');
                accessMessage.classList.remove('hidden');
            }, 10);
        }, 200); 
    }

    const closeButton = document.querySelector('.modal-close-error');
    closeButton?.addEventListener('click', closeModalError);

    function closeModalError() {
        if (accessMessage) {
            accessMessage.classList.remove('show');
            accessMessage.style.transform = 'translateY(-30px)'; 
            accessMessage.classList.add('hidden');

            setTimeout(() => {
                accessMessage.style.display = 'none'; 
            }, 500); 
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModalError();
        }
    });
});
