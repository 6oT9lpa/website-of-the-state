function hideContent(contentId) {
    const contentElement = document.getElementById(contentId);
    if (contentElement) {
        contentElement.classList.remove('fade-in');
        contentElement.innerHTML = '';
    }
}

function loadContent(url, contentId, activeButtonId) {
    if (contentId === 'attorney-content') {
        hideContent('judicial-content');
        hideContent('other-content');
    } else if (contentId === 'judicial-content') {
        hideContent('attorney-content');
        hideContent('other-content');
    } else if (contentId === 'other-content') {
        hideContent('attorney-content');
        hideContent('judicial-content');
    }

    const buttons = document.querySelectorAll('.nav-button');
    buttons.forEach(button => button.classList.remove('active-button'));

    document.getElementById(activeButtonId).classList.add('active-button');

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.text();
        })
        .then(data => {
            const contentElement = document.getElementById(contentId);
            if (contentElement) {
                contentElement.innerHTML = data;
                contentElement.classList.add('fade-in');
            }
        })
        .catch(error => console.error('Ошибка загрузки контента:', error));
}

document.getElementById('load-prosecution-office').addEventListener('click', function(event) {
    event.preventDefault();
    loadContent('/get_prosecution_office_content', 'attorney-content', 'load-prosecution-office');
});

document.getElementById('load-judicial-office').addEventListener('click', function(event) {
    event.preventDefault();
    loadContent('/get_judicial_office_content', 'judicial-content', 'load-judicial-office');
});

document.addEventListener('DOMContentLoaded', () => {
    const message = sessionStorage.getItem('notification');
    const isError = sessionStorage.getItem('isError') === 'true';

    if (message) {
        showNotification(message, isError);

        sessionStorage.removeItem('notification');
        sessionStorage.removeItem('isError');
    }
});


document.querySelector('.delete-link')?.addEventListener('click', function(e) {
    e.preventDefault();
    
    const url = e.target.href;

    fetch(url, {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/doc';

            sessionStorage.setItem('notification', data.message);
            sessionStorage.setItem('isError', 'false');
        } else {
            showNotification(data.message, true);
        }
    })
    .catch(error => {
        console.error('Произошла ошибка:', error);
        showNotification('Произошла ошибка при отправке данных', true);
    });
});
