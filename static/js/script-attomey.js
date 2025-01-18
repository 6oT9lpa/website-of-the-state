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

const observer = new MutationObserver((mutationsList) => {
    mutationsList.forEach((mutation) => {
        if (mutation.type === 'childList') {
            const modal = document.getElementById('modal-prosecutor');
            if (modal) {
                console.log('Modal dynamically added to DOM');
                observer.disconnect(); 
            }
        }
    });
});

observer.observe(document.body, { childList: true, subtree: true });

function showErrorJustice(input, message) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = message;
        formControl.classList.add('error'); 
    }
}

function clearErrorJustice(input) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = ''; 
        formControl.classList.remove('error'); 
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

    document.addEventListener('click', (e) => { 
        console.log(e.target.id);
        if (e.target.id === 'modal-open-btn') {
            e.preventDefault();
            showModal('modal-prosecutor');
        }

        if (e.target.id === 'close-modal-btn') {
            e.preventDefault();
            hideModal('modal-prosecutor');
        }
    });

    document.addEventListener('input', (e) => {
        if (e.target.id === 'evidence') {
            const input = e.target;
            const links = input.value.trim().split(/\s+/);

            const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=[\w-]+|.+)$/;
            const rutubeRegex = /^(https?:\/\/)?(www\.)?rutube\.ru\/video\/[a-zA-Z0-9]+\/?$/;
            const yapixRegex = /^(https?:\/\/)?(www\.)?yapix\.ru\/video\/[a-zA-Z0-9]+\/?$/;
            const imgurRegex = /^(https?:\/\/)?(www\.)?imgur\.com\/[a-zA-Z0-9]+\/?$/;

            if (input.value === '') {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }

            const invalidLinks = links.filter(link => 
                !youtubeRegex.test(link) && 
                !rutubeRegex.test(link) && 
                !yapixRegex.test(link) && 
                !imgurRegex.test(link)
            );

            if (invalidLinks.length > 0) {
                const errorMessage = `Некорректные ссылки: ${invalidLinks.join(', ')}`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }
        } else if (e.target.id === 'defendant') {
            const input = e.target;

            if (input.value === '') {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }

            const nameStaticPattern = /^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$/;
            const factionStaticPattern = /^(LSPD|LSCSD|FIB|SANG|EMS|WN|GOV) \d{1,7}$/;
            if (!nameStaticPattern.test(input.value) && !factionStaticPattern.test(input.value)) { 
                showError(input, 'Введите данные в формате "Nick Name static" или "LSPD, LSCSD, FIB, SANG, EMS, WN, GOV static".');
                return;
            }
            else {
                clearError(input);
            }
        } else if (e.target.id === 'phone') {
            const input = e.target;

            if (input.value === '') {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }
        } else if (e.target.id === 'card') {
            const input = e.target;

            if (input.value === '') {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }
        } else if (e.target.id === 'claim') {
            const input = e.target;

            if (input.value === '') {
                const errorMessage = `Поле не может быть пустым!`;
                showError(input, errorMessage);
                return;
            } else {
                clearError(input);
            }
        } else if (e.target.id === 'lower') {
            const input = e.target;
        
            if (input.value !== '') {
                const nameStaticPattern = /^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$/;
                if (!nameStaticPattern.test(input.value)) {
                    showError(input, 'Введите данные в формате "Nick Name static"');
                    return;
                }
                else {
                    clearError(input);
                }
            } else {
                clearError(input);
            }
        } else if (e.target.id === 'static') {
            const input = e.target;

            if (input.value !== '') {
                showError(input, `Поле не может быть пустым!`);

                const staticPattern = /^\d{1,7}$/;
                if (!staticPattern.test(input.value)) {
                    showError(input, 'Введите данные в численном формате до 7 символов');
                    return;
                }
                else {
                    clearError(input);
                }
            }
            else {
                clearError(input);
            }

        }  else if (e.target.id === 'nickname') {
            const input = e.target;

            if (input.value !== '') {
                showError(input, `Поле не может быть пустым!`);
                
                const nicknamePattern = /^[A-Z][a-z]+ [A-Z][a-z]+$/;
                if (!nicknamePattern.test(input.value)) {
                    showError(input, 'Введите данные в формате "Nick Name"');
                    return;
                }
                else {
                    clearError(input);
                }
            }
            else {
                clearError(input);
            }
            
        }
    });

    document.addEventListener('submit', (e) => {
        if (e.target.id === 'create-petition-prosecutor') {
            e.stopPropagation();
            e.preventDefault();
            const formData = new FormData(e.target);
            const defendants = formData.getAll('defenda'); 
            const data = Object.fromEntries(formData.entries());

            console.log(data);

            const payload = {
                ...data, 
                defendants: defendants
            };

            fetch('/create_petition_prosecutor', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
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
                showNotification('Произошла ошибка. Попробуйте позже!', true);
            });
        }
    });
});
