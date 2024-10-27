document.addEventListener('DOMContentLoaded', () => {
    const access_message = document.querySelector('#access-message');
    
    if (access_message) {
        access_message.classList.add('hidden'); // Изначально скрываем
        setTimeout(() => {
            access_message.style.display = 'block'; 
            access_message.style.transform = 'translateY(30px)';
            setTimeout(() => {
                access_message.style.transform = 'translateY(0px)';
                access_message.classList.add('show');
                access_message.classList.remove('hidden'); // Убираем класс hidden после показа
            }, 10); 
        }, 200); // Измените на желаемую задержку
    }

    document.querySelector('.modal-close-error')?.addEventListener('click', closeModal_error);

    function closeModal_error() {
        if (access_message) {
            access_message.classList.remove('show');
            access_message.style.transform = 'translateY(-30px)';
            access_message.classList.add('hidden');
            setTimeout(() => {
                access_message.style.display = 'none'; 
            }, 500); 
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal_error();
        }
    });
});
