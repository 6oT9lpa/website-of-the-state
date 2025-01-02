document.addEventListener('DOMContentLoaded', () => {
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
            const action = e.target.dataset.action;
            document.querySelectorAll("#" + hiddenInputId).forEach(i => i.value = action) ;
            dropdown.classList.remove('open');
            dropdownBtn.classList.remove('active');
            showModal(document.querySelector('#modal-1'));
            document.querySelector('#close-btn-1').addEventListener('click', () => hideModal(document.querySelector('#modal-1')));
            updateContentSettings();
        });
    }

    function updateContentSettings() {
        const action = document.getElementById('action-0').value;

        if (action === 'nickname') {
            document.querySelector('.settings-nickname').style.display = 'flex';
            document.querySelector('.settings-password').style.display = 'none';
            document.querySelector('.settings-discordID').style.display = 'none';

        }  else if (action === 'password') {
            document.querySelector('.settings-nickname').style.display = 'none';
            document.querySelector('.settings-password').style.display = 'flex';
            document.querySelector('.settings-discordID').style.display = 'none';

        }   else if (action === 'discord') {
            document.querySelector('.settings-nickname').style.display = 'none';
            document.querySelector('.settings-password').style.display = 'none';
            document.querySelector('.settings-discordID').style.display = 'flex';
        }
    }

    setupDropdown(document.querySelector('#dropdown-0'), document.querySelector('#dropdown-btn-0'), document.querySelector('#dropdown-menu-0'), 'action-0');

});


document.getElementById('settings-nickname-form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(event.target);

    fetch('/profile_settings', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
    },
        body: JSON.stringify(Object.fromEntries(formData.entries()))
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

document.getElementById('settings-password-form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(event.target);

    fetch('/profile_settings', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
    },
        body: JSON.stringify(Object.fromEntries(formData.entries()))
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

document.getElementById('settings-discordID-form').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(event.target);
    fetch('/profile_settings', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
    },
        body: JSON.stringify(Object.fromEntries(formData.entries()))
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