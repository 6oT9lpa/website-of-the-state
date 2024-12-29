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
            document.getElementById(hiddenInputId).value = action;
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