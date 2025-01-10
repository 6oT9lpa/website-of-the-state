const modals = [
    { openBtn: '#open-btn-1', closeBtn: '#close-btn-1', modal: '#modal-1' }
]

function setupModalToggle(openBtn, closeBtn, modal) {
    if (openBtn && closeBtn && modal) {
        openBtn.addEventListener('click', () => showModal(modal));
        closeBtn.addEventListener('click', () => hideModal(modal));
    }
}

modals.forEach(({ openBtn, closeBtn, modal }) => {
    setupModalToggle(document.querySelector(openBtn), document.querySelector(closeBtn), document.querySelector(modal));
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