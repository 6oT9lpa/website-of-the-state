
function showModal(modal) {
    modal.style.display = 'flex';
    document.querySelectorAll('#overlay').forEach(o => {
        o.classList.add('active');
    });

    setTimeout(() => {
        modal.classList.remove('hidden-modal');
        modal.classList.add('show-modal');
    }, 10);
}

function hideModal(modal) {
    modal.classList.remove('show-modal');
    modal.classList.add('hidden-modal');

    setTimeout(() => {
        modal.style.display = 'none';
        document.querySelectorAll('#overlay').forEach(o => {
            o.classList.remove('active');
        });
    }, 450);
}

const modals = [
    { openBtn: '#open-modal-1', closeBtn: '#close-btn-1', modal: '#modal-1' }
];

function setupModalToggle(openBtn, closeBtn, modal) {
    if (openBtn && closeBtn && modal) {
        openBtn.addEventListener('click', () => showModal(modal));
        closeBtn.addEventListener('click', () => hideModal(modal));
    }
}

modals.forEach(({ openBtn, closeBtn, modal }) => {
    setupModalToggle(document.querySelector(openBtn), document.querySelector(closeBtn), document.querySelector(modal));
});

function setupDropdown(dropdown, dropdownBtn, dropdownMenu, hiddenInputId) {
    if (!dropdown || !dropdownBtn || !dropdownMenu) return;

    dropdownBtn.addEventListener('click', (e) => {
        e.preventDefault();
        dropdown.classList.toggle('open');
        dropdownBtn.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target) && !dropdownBtn.contains(e.target)) {
            dropdown.classList.remove('open');
            dropdownBtn.classList.remove('active');
        }
    });

    dropdownMenu.addEventListener('click', (e) => {
        e.preventDefault();

        if (e.target.classList.contains('disabled')) {
            return;
        }
        
        const action = e.target.dataset.action;
        dropdownBtn.textContent = e.target.textContent;
        document.getElementById(hiddenInputId).value = action;
        dropdown.classList.remove('open');
        dropdownBtn.classList.remove('active');
    });
}

setupDropdown(document.querySelector('#dropdown-1'), document.querySelector('#dropdown-btn-1'), document.querySelector('#dropdown-menu-1'), 'action-1');

const fileInput = document.getElementById("file-upload");
const fileNameSpan = document.getElementById("file-name");

function updateFileName() {
    var fileInput = document.getElementById('file-upload');
    var fileName = document.getElementById('file-name');
    fileName.textContent = fileInput.files.length > 0 ? fileInput.files[0].name : 'Файл не выбран';
}

document.addEventListener('DOMContentLoaded', () => {
    const message = sessionStorage.getItem('notification');
    const isError = sessionStorage.getItem('isError') === 'true';

    if (message) {
        showNotification(message, isError);
        sessionStorage.removeItem('notification');
        sessionStorage.removeItem('isError');
    }
});

const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
document.querySelectorAll('#datetime').forEach(element => {
    const dateStr = element.textContent;
    const date = new Date(dateStr);
    const formattedDate = date.toLocaleDateString('ru-RU', options);
    element.textContent = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
});

const news_container = {
    admin: document.querySelector('#admin'),
    weazel: document.querySelector('#weazel'),
    gov: document.querySelector('#gov'),
};

function toggleNews(container) {
    console.log(container);
    if (!container) return;

    Object.values(news_container).forEach(news => {
        news.classList.remove('show')
        news.classList.add('hidden')

        setTimeout(() => {
            if (news) news.style.display = 'none';
        }, 250);
    });
    setTimeout(() => {
        container.style.display = 'grid';
        setTimeout(() => {
            container.classList.remove('hidden')
            container.classList.add('show')
        }, 10);
    }, 250);

    document.querySelectorAll('.nav-button').forEach(button => {
        button.classList.remove('active');
    });

    if (container === news_container.admin) {
        document.querySelector('.nav-button:nth-child(1)').classList.add('active');
    } else if (container === news_container.gov) {
        document.querySelector('.nav-button:nth-child(2)').classList.add('active');
    } else if (container === news_container.weazel) {
        document.querySelector('.nav-button:nth-child(3)').classList.add('active');
    }
}


document.querySelector('#create-news').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    fetch('/create_news', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            sessionStorage.setItem('notification', data.message);
            sessionStorage.setItem('isError', 'false');
            window.location.reload();
        } else {
            showNotification(data.message, true);
        }
    })
    .catch(error => {
        console.error('Произошла ошибка:', error);
        showNotification('Произошла ошибка при отправке данных', true);
    });
});

document.addEventListener('DOMContentLoaded', function(e){
    const readMoreButtons = document.querySelectorAll('.read-more');
    const modal = document.getElementById('modal-2');
    const modalContent = modal.querySelector('.content-modal');
    const overlay = document.querySelector('#overlay')
    const closeButtons = document.querySelectorAll('.btn-close');

    readMoreButtons.forEach(button => {
        button.addEventListener('click', event => {
            event.preventDefault();

            const newsId = button.getAttribute('data-news-id');
            const author = button.getAttribute('data-author');
            const heading = button.getAttribute('data-heading');
            const fullContent = button.getAttribute('data-full-content');
            const datetime = button.getAttribute('data-datetime');
            const filePath = button.getAttribute('data-file-path');

            document.getElementById('modal-heading').textContent = heading;
            document.getElementById('modal-full-content').textContent = fullContent;
            document.getElementById('modal-creator').textContent = 'Создатель: ' + author;
            document.getElementById('modal-datetime').textContent = 'Дата и время: ' + datetime;
            document.getElementById('modal-image').src = filePath ? '/static/uploads/images/' + filePath : '/static/uploads/images/maxresdefault.jpg';

            modal.style.display = 'flex';
            setTimeout(() => {
                modal.classList.remove('hidden-modal');
                modal.classList.add('show-modal');
                overlay.classList.add('active');
            }, 10);
        });
    });

    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('btn-close')) {
            modal.classList.add('hidden-modal');
            modal.classList.remove('show-modal');
            overlay.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    });
    
    modal.addEventListener('click', event => {
        if (event.target === modal) {
            modal.classList.add('hidden-modal');
            modal.classList.remove('show-modal');
            overlay.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
        }
    });
});

window.onload = function () {
    loadDefaultContent();
};

function loadDefaultContent() {
    document.getElementById("admin").style.display = "grid";
    setTimeout(() => {
        document.querySelector('.nav-button:nth-child(1)').classList.add('active');
    }, 10);
    
}
