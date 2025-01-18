document.documentElement.style.setProperty('--screen-width', `${window.innerWidth}px`);
document.documentElement.style.setProperty('--screen-height', `${window.innerHeight}px`);

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get('uid');
    document.querySelectorAll('#uidcompliant').forEach(inp => {
        inp.value = uid;
    });

    let isHovered = false;
    let isAnimating = false;
    let hoverTimeout;

    const sidebar = document.querySelector('.sidebar-container');
    const maincontent = document.querySelector('.main-content-complaint');

    function isMobile() {
        return window.innerWidth < 1025;
    }

    const complaintBtns = document.querySelectorAll('.complaint-btn input');
    function isButton(target) {
        return Array.from(complaintBtns).some(btn => btn === target || btn.contains(target));
    }

    sidebar.addEventListener('mouseenter', (event) => {
        if (isMobile()) return;
        if (isHovered || isAnimating || isButton(event.target)) return;
        isHovered = true;
        isAnimating = true;

        clearTimeout(hoverTimeout);
        sidebar.classList.remove('hover-out');
        hoverTimeout = setTimeout(() => {
            sidebar.classList.add('hover-in');
            hoverTimeout = setTimeout(() => {
                isAnimating = false;
            }, 1000);
            hoverTimeout = setTimeout(() => {
                maincontent.style.width = 'calc(var(--screen-width) - 300px)';
            }, 200);
        }, 100);
    });

    sidebar.addEventListener('mouseleave', (event) => {
        if (isMobile()) return;
        if (!isHovered || isAnimating || isButton(event.target)) return;
        isHovered = false;
        isAnimating = true;

        clearTimeout(hoverTimeout);
        sidebar.classList.remove('hover-in');
        hoverTimeout = setTimeout(() => {
            sidebar.classList.add('hover-out');
            hoverTimeout = setTimeout(() => {
                isAnimating = false;
            }, 1000);
            hoverTimeout = setTimeout(() => {
                maincontent.style.width = 'calc(var(--screen-width) - 400px)';
            }, 80);
        }, 100);
    });

    sidebar.addEventListener('click', (event) => {
        if (isMobile()) return;
        if (isButton(event.target)) return;
        sidebar.classList.toggle('open');
        maincontent.style.width = 'calc(var(--screen-width) - 400px)';
        maincontent.classList.toggle('open');
    });

});

document.querySelector('#claim-processing')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const decisions = formData.getAll('decision'); 
    const payload = {
        ...Object.fromEntries(formData.entries()), 
        decision: decisions
    };

    const validProcessing = ['accept', 'reject', 'hold'];
    if (!validProcessing.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите обстоятельства', true);
        return;
    }

    if (!data.consideration || !data.consideration.trim()) {   
        showNotification('Введите рассмотрение, ссылаясь на закон', true);
        return;
    }

    fetch('/create_court_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);

            setTimeout(() => {
                location.reload();
            }, 3000);
        } else {
            showNotification(data.message, true);
        }
    })
    .catch(error => {
        console.error('Произошла ошибка:', error);
        showNotification('Произошла ошибка при отправке данных', true);
    });
});

const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
document.querySelectorAll('#datetime').forEach(element => {
    const dateStr = element.textContent;
    const date = new Date(dateStr);
    const formattedDate = date.toLocaleDateString('ru-RU', options);
    element.textContent = 'Дата: ' + formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
});

function showError(input, message) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = message;
        formControl.className = 'form-input error'; 
    } 
}

function clearError(input) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = ''; 
        formControl.className = 'form-input'; 
    }
}

document.addEventListener('DOMContentLoaded', () => {    
    const message = sessionStorage.getItem('notification');
    const isError = sessionStorage.getItem('isError') === 'true';

    if (message) {
        showNotification(message, isError);
        sessionStorage.removeItem('notification');
        sessionStorage.removeItem('isError');
    }
    
    document.addEventListener('input', (event) => {
        if (event.target.id === 'articles') {
            const input = event.target
            if (input.value != '') {
                const regex = /^(?:\d{1,2}(?:\.\d{1,2}){0,2}\s*(?:УК|АК))(?:,\s*\d{1,2}(?:\.\d{1,2}){0,2}\s*(?:УК|АК))*$/;
                if (!regex.test(input.value)) {
                    showError(input, 'Неверный формат. Должен быть x.x УК/АК, xx.x УК/АК, x.xx УК/АК, xx.xx УК/АК или x.x.x УК/АК, разделенные запятыми.');
                    return;
                    
                } else {
                    clearError(input)
                }
            } else {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            }
        }
        if (event.target.id === 'link') {
            const input = event.target
            if (input.value != '') { 
                const regex = /^https:\/\/docs\.google\.com\/document\/.*/;
                if (!regex.test(input.value)) {
                    showError(input, 'Неверный формат. Ссылка не указываетс на google docs');
                    return;
                    
                } else {
                    clearError(input);
                }
            }
            else {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            }
        }
        if (event.target.id === 'numworked') {
            const input = event.target
            if (input.value === '') { 
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            }
            else {
                clearError(input);
            }
        }
    });
});

document.getElementById('processing-prosecutor')?.addEventListener('submit', (e) => {
    e.preventDefault();
    e.stopPropagation();

    const confirmDialog = document.getElementById('custom-confirm');
    confirmDialog.style.display = 'flex';
    setTimeout(() => {
        confirmDialog.classList.remove('hidden');
        confirmDialog.classList.add('show');
    }, 10);

    document.getElementById('confirm-yes').onclick = () => {
        confirmDialog.classList.remove('show');
        confirmDialog.classList.add('hidden');
        setTimeout(() => {
            confirmDialog.style.display = 'none';
        }, 300);

        const action = e.submitter.name === 'action_accept' ? 'accept' : 'reject';
        fetch('/process-complaint-prosecutor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 
            },
            body: JSON.stringify({
                uid: document.getElementById('uidcompliant').value,
                action: action,
            }),
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
    };

    document.getElementById('confirm-no').onclick = () => {
        confirmDialog.classList.remove('show');
        confirmDialog.classList.add('hidden');
        setTimeout(() => {
            confirmDialog.style.display = 'none';
        }, 300);
    };
});


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

document.getElementById('completed-prosecutor').addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopPropagation();

    const action = e.submitter.name;
    const uid = document.getElementById('uidcompliant').value;
    const confirmDialog = document.getElementById('custom-confirm');

    confirmDialog.style.display = 'flex';
    setTimeout(() => {
        confirmDialog.classList.remove('hidden');
        confirmDialog.classList.add('show');
    }, 10);

    document.getElementById('confirm-yes').onclick = () => {
        confirmDialog.classList.remove('show');
        confirmDialog.classList.add('hidden');
        setTimeout(() => {
            confirmDialog.style.display = 'none';
        }, 300);

        if (action === 'violations_order' || action === 'violations_district_court' || action === 'violations_supreme_court' ) {
            const modal = document.getElementById('modal-1');
            showModal(modal);

            document.getElementById('close-btn-1').addEventListener('click', (e) => {
                hideModal(modal);
            });

            document.getElementById('completed-petition').onsubmit = function (modalEvent) {
                modalEvent.preventDefault();
                sendDataToServer(uid, action);
                hideModal(modal);
            };
        } else {
            sendDataToServer(uid, action);
        }
    };

    document.getElementById('confirm-no').onclick = () => {
        confirmDialog.classList.remove('show');
        confirmDialog.classList.add('hidden');
        setTimeout(() => {
            confirmDialog.style.display = 'none';
        }, 300);
    };
});

function sendDataToServer(uid, actionValue) {
    fetch('/violations-prosecutor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            uid: uid,
            action: actionValue,
            numworked: document.getElementById('numworked').value || null,
            link: document.getElementById('link').value || null,
            articles: document.getElementById('articles').value || null,
        }),
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
        showNotification('Произошла ошибка при отправке данных', true);
    });
}
