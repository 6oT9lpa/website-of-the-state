document.addEventListener('DOMContentLoaded', () => {    
    let claimCounter = 1;

    document.addEventListener('click', (e) => {
        // Добавление искового требования
        if (e.target.id === 'addClaim') {
            e.preventDefault();

            const groupClaimDiv = document.querySelector('.group-claim');
            if (!groupClaimDiv) return;

            groupClaimDiv.classList.add('active-grid');
            const newClaimDiv = document.createElement("div");
            newClaimDiv.classList.add("content-claim");

            const newLabel = document.createElement("label");
            newLabel.setAttribute("for", `claims_${claimCounter}`);
            newLabel.textContent = "Исковое требование.";

            const newFormInputDiv = document.createElement("div");
            newFormInputDiv.classList.add("form-input");
            newFormInputDiv.id = `claim-input-${claimCounter}`;

            const newInput = document.createElement("input");
            newInput.type = "text";
            newInput.id = `claim`;
            newInput.name = "claims";
            newInput.placeholder = "Введите требование";

            newFormInputDiv.appendChild(newInput);

            const newSpan = document.createElement("span");
            newSpan.classList.add("text-danger");
            newSpan.id = `is-invalid`;

            newClaimDiv.appendChild(newLabel);
            newClaimDiv.appendChild(newFormInputDiv);
            newClaimDiv.appendChild(newSpan);

            groupClaimDiv.appendChild(newClaimDiv);

            claimCounter++;

            const deleteButton = document.querySelector('#btn-add-claim');
            if (deleteButton) {
                deleteButton.style.display = "inline-block";
            }
        }

        // Удаление искового требования
        if (e.target.id === 'btn-add-claim') {
            e.preventDefault();

            const groupClaimDiv = document.querySelector('.group-claim');
            if (!groupClaimDiv) return;

            const lastClaimDiv = groupClaimDiv.querySelector(".content-claim:last-of-type");
            if (lastClaimDiv) {
                lastClaimDiv.remove();
                claimCounter--;
                if (claimCounter <= 1) {
                    e.target.style.display = "none";
                    groupClaimDiv.classList.remove('active-grid');
                }
            }
        }

        // Выпадающее меню
        const dropdownBtn = document.querySelector('#dropdown-btn-0');
        const dropdownMenu = document.querySelector('#dropdown-0');

        if (e.target === dropdownBtn) {
            e.preventDefault();
            dropdownMenu.classList.toggle('open');
            dropdownBtn.classList.toggle('active');
        }

        if (e.target.closest('#dropdown-menu-0')) {
            if (e.target.tagName === 'A') {
                e.preventDefault();
                const action = e.target.dataset.action;
                dropdownBtn.textContent = e.target.textContent;
                document.getElementById('action-0').value = action;
                dropdownMenu.classList.remove('open');
                dropdownBtn.classList.remove('active');
                updateContentProsecutor('action-0');
            }
        } else if (!e.target.closest('.dropdown')) {
            dropdownMenu?.classList.remove('open');
            dropdownBtn?.classList.remove('active');
        }

        // Модальное окно
        if (e.target.id === 'create-btn-district') {
            e.preventDefault();
            showModal('modal-court');
        }

        if (e.target.id === 'btn-modal-close') {
            e.preventDefault();
            hideModal('modal-court');
        }

        // Добавление и удаление ответчиков
        if (e.target.id.startsWith('addDefenda')) {
            e.preventDefault();
            const groupId = e.target.id.includes('criminal') ? 'criminal-group-defenda' : 'complaint-group-defenda';
            const buttonId = e.target.id.includes('criminal') ? 'btn-add-defenda-criminal' : 'btn-add-defenda-complaint';
            handleAddDefenda(groupId, buttonId);
        }

        if (e.target.id.startsWith('btn-add-defenda')) {
            e.preventDefault();
            const groupId = e.target.id.includes('criminal') ? 'criminal-group-defenda' : 'complaint-group-defenda';
            const buttonId = e.target.id.includes('criminal') ? 'btn-add-defenda-criminal' : 'btn-add-defenda-complaint';
            handleRemoveDefenda(groupId, buttonId);
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideModal();
        }
    });
});

function updateContentProsecutor(hiddenInputId) {
    let action = document.getElementById(hiddenInputId);
    let criminalPage = document.getElementById('criminal');
    let complaintPage = document.getElementById('complaint');

    if (action.value === 'criminal_case') {
        complaintPage.style.display = 'none';
        criminalPage.style.display = 'flex';
    } else if (action.value === 'common_complaint') {
        criminalPage.style.display = 'none';
        complaintPage.style.display = 'flex';
    } else {
        return;
    }
}

function handleAddDefenda(groupId, deleteButtonId) {
    const groupDefendaDiv = document.getElementById(groupId);
    if (!groupDefendaDiv) return;
    
    const newContentDiv = document.createElement("div");
    newContentDiv.classList.add("content-defenda");

    const newFormInputDiv = document.createElement("div");
    newFormInputDiv.classList.add("form-input");

    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "defenda";
    newInput.id = 'defendant';
    newInput.placeholder = "Введите ник и статик";

    newFormInputDiv.appendChild(newInput);

    const newSpan = document.createElement("span");
    newSpan.classList.add("text-danger");
    newSpan.id = `is-invalid`;

    newContentDiv.appendChild(newFormInputDiv);
    newContentDiv.appendChild(newSpan);

    groupDefendaDiv.appendChild(newContentDiv);

    const deleteButton = document.getElementById(deleteButtonId);
    if (deleteButton) {
        deleteButton.style.display = "inline-block";
    }
}

function handleRemoveDefenda(groupId, deleteButtonId) {
    const groupDefendaDiv = document.getElementById(groupId);
    if (!groupDefendaDiv) return;

    const lastDefendaDiv = groupDefendaDiv.querySelector(".content-defenda:last-of-type");
    if (lastDefendaDiv) {
        lastDefendaDiv.remove();
    }

    if (groupDefendaDiv.querySelectorAll(".content-defenda").length < 2) {
        const deleteButton = document.getElementById(deleteButtonId);
        if (deleteButton) {
            deleteButton.style.display = "none";
        }
    }
}
function showModal(modal) {
    const modalDistrict = document.getElementById(modal);
    const overlay = document.getElementById('overlay');

    if (modalDistrict && overlay) {
        modalDistrict.style.display = 'flex';
        overlay.classList.add('active');

        setTimeout(() => {
            modalDistrict.classList.remove('hidden-modal');
            modalDistrict.classList.add('show-modal');
        }, 10);
    }
}

function hideModal(modal) {
    const modalDistrict = document.getElementById(modal);
    const overlay = document.getElementById('overlay');

    if (modalDistrict && overlay) {
        modalDistrict.classList.remove('show-modal');
        modalDistrict.classList.add('hidden-modal');

        setTimeout(() => {
            modalDistrict.style.display = 'none';
            overlay.classList.remove('active');
        }, 450);
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
});

function FetchClick(e) {
    e.preventDefault();

    const form = e.target.closest('form');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const defenda = formData.getAll('defenda'); 
    const claims = formData.getAll('claims');

    defenda.forEach(d => { 
        if (d == '') {
            showNotification('Поле "ответчик" не может быть пустым.', true);
        }

        const pattern = /^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$/;
        if (!pattern.test(d)) {
            showNotification('Введите данные в формате "Nick Name static"');
        }
    });

    claims.forEach(claim => {
        if (claim == '') {
            showNotification('Поле "исковые требования" не может быть пустым.', true);
        }
    });

    const validType = ['criminal_case', 'common_complaint'];
    if (isProsecutor) {
        if (!validType.includes(data.action)) {
            showNotification('Выберите действие', true);
            return;
        }
    }

    if (!data['phone-plaintiff'] || !data['phone-plaintiff'].trim()) {
        showNotification('Поле "номер телефона" не может быть пустым.', true);
    }

    if (!data['card'] || !data['card'].trim()) {
        showNotification('Поле "номер карта" не может быть пустым.', true);
    }

    if (!data['description'] || !data['description'].trim()) {
        showNotification('Поле "ситуации" не может быть пустым.', true);
    }

    const payload = {
        ...data, 
        defenda: defenda, 
        claims: claims
    };

    fetch('/create-claim-state', {
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
        showNotification('Произошла ошибка. Пожалуйста, попробуйте снова.', true);
    });
};

