const judicialOfficeButton = document.getElementById('load-judicial-office');
const prosecutionOfficeButton = document.getElementById('load-prosecution-office');
const otherDepartmentsButton = document.getElementById('load-other-office');
const districtButtons1 = document.getElementById('load-claim-district');
const districtButtons2 = document.getElementById('load-claim-supreme');
const backButton = document.createElement('a');
backButton.textContent = 'Назад';
backButton.classList.add('nav-button', 'back-button');
backButton.style.display = 'none';
const supremeButton = document.getElementById('load-claim-supreme');
const districtButton = document.getElementById('load-claim-district');
const attorneyContent = document.getElementById('judicial-content');

document.addEventListener('DOMContentLoaded', () => {
    const savedButtonId = sessionStorage.getItem('selectedButton');
    const savedUrl = sessionStorage.getItem('selectedUrl');

    if (savedButtonId && savedUrl) {
        toggleContent(savedButtonId, savedUrl);
    }
    restoreState();
});
document.querySelector('.navbar').prepend(backButton);

function saveState(state) {
    localStorage.setItem('officeState', state);
}

function restoreState() {
    const state = localStorage.getItem('officeState');
    if (state === 'showjudicialOffice') {
        showJudicialOffice();
    } else {
        attorneyContent.innerHTML = '';
        attorneyContent.classList.remove('fade-in');
        [supremeButton, districtButton].forEach(button => {
            button.classList.remove('active-button');
        });
    }
}

function showJudicialOffice() {
    prosecutionOfficeButton.classList.remove('fade-in-nav');
    otherDepartmentsButton.classList.remove('fade-in-nav');
    judicialOfficeButton.classList.remove('fade-in-nav');
    
    prosecutionOfficeButton.classList.add('hidden-nav');
    otherDepartmentsButton.classList.add('hidden-nav');
    judicialOfficeButton.classList.add('hidden-nav');
   
    prosecutionOfficeButton.style.transform = 'translateX(300px)';
    otherDepartmentsButton.style.transform = 'translateX(-300px)';
    setTimeout(() => { 
        prosecutionOfficeButton.style.display = 'none';
        otherDepartmentsButton.style.display = 'none';
        judicialOfficeButton.style.display = 'none';
    }, 300);

    setTimeout(() => {
        districtButtons1.style.display = 'block';
        districtButtons2.style.display = 'block';

        setTimeout(() => {
            districtButtons1.classList.remove('hidden-nav');
            districtButtons1.classList.add('fade-in-nav'); 
            districtButtons2.classList.remove('hidden-nav');
            districtButtons2.classList.add('fade-in-nav');
            backButton.classList.add('nav-button');
            backButton.style.display = 'block';
        }, 300);
    }, 300);
}

judicialOfficeButton.addEventListener('click', () => {
    saveState('showjudicialOffice');
    showJudicialOffice();
});

backButton.addEventListener('click', () => {
    localStorage.removeItem('officeState');
    sessionStorage.removeItem('selectedButton');
    sessionStorage.removeItem('selectedUrl');

    [supremeButton, districtButton].forEach(button => {
        button.classList.remove('active-button');
    });
    
    attorneyContent.innerHTML = '';
    attorneyContent.classList.remove('fade-in');

    districtButtons1.classList.add('hidden-nav');
    districtButtons1.classList.remove('fade-in-nav'); 
    districtButtons2.classList.add('hidden-nav');
    districtButtons2.classList.remove('fade-in-nav');
    backButton.classList.remove('nav-button');
    backButton.style.display = 'none';

    setTimeout(() => {
        districtButtons1.style.display = 'none';
        districtButtons2.style.display = 'none';
    }, 300);

    setTimeout(() => {
        prosecutionOfficeButton.style.display = 'block';
        otherDepartmentsButton.style.display = 'block';
        judicialOfficeButton.style.display = 'block';
        setTimeout(() => { 
            prosecutionOfficeButton.classList.add('fade-in-nav');
            otherDepartmentsButton.classList.add('fade-in-nav');
            judicialOfficeButton.classList.add('fade-in-nav');
            
            prosecutionOfficeButton.classList.remove('hidden-nav');
            otherDepartmentsButton.classList.remove('hidden-nav');
            judicialOfficeButton.classList.remove('hidden-nav');

            prosecutionOfficeButton.style.transform = 'translateX(0px)';
            otherDepartmentsButton.style.transform = 'translateX(0px)';
        }, 15);   
    }, 300);
});

function toggleContent(buttonId, url) {
    sessionStorage.setItem('selectedButton', buttonId);
    sessionStorage.setItem('selectedUrl', url);

    [supremeButton, districtButton].forEach(button => {
        button.classList.remove('active-button');
    });

    attorneyContent.innerHTML = '';
    attorneyContent.classList.remove('fade-in');

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сети');
            }
            return response.text();
        })
        .then(data => {
            attorneyContent.innerHTML = data;
            attorneyContent.classList.add('fade-in');
            document.getElementById(buttonId).classList.add('active-button');
        })
        .catch(error => console.error('Ошибка загрузки контента:', error));
}

supremeButton.addEventListener('click', function(event) {
    event.preventDefault();
    toggleContent('load-claim-supreme', '/get-claim-supreme-content');
});

districtButton.addEventListener('click', function(event) {
    event.preventDefault();
    toggleContent('load-claim-district', '/get-claim-district-content');
});


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
            newFormInputDiv.classList.add("form-input-modal");
            newFormInputDiv.id = `claim-input-${claimCounter}`;

            const newInput = document.createElement("input");
            newInput.type = "text";
            newInput.id = `claim`;
            newInput.name = "claims[]";
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
            dropdownMenu.classList.remove('open');
            dropdownBtn.classList.remove('active');
        }

        // Модальное окно
        if (e.target.id === 'create-btn-district') {
            e.preventDefault();
            showModal();
        }

        if (e.target.id === 'btn-modal-close') {
            e.preventDefault();
            hideModal();
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
    
    groupDefendaDiv.classList.add('active-grid');
    const newContentDiv = document.createElement("div");
    newContentDiv.classList.add("content-defenda");

    const newLabel = document.createElement("label");
    newLabel.textContent = "Ответчик.";

    const newFormInputDiv = document.createElement("div");
    newFormInputDiv.classList.add("form-input-modal");

    const newInput = document.createElement("input");
    newInput.type = "text";
    newInput.name = "defenda[]";
    newInput.placeholder = "Введите ник и статик";

    newFormInputDiv.appendChild(newInput);

    const newSpan = document.createElement("span");
    newSpan.classList.add("text-danger");

    newContentDiv.appendChild(newLabel);
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

    if (groupDefendaDiv.querySelectorAll(".content-defenda").length <= 1) {
        const deleteButton = document.getElementById(deleteButtonId);
        if (deleteButton) {
            deleteButton.style.display = "none";
            groupDefendaDiv.classList.remove('active-grid');
        }
    }
}
function showModal() {
    const modalDistrict = document.getElementById('modal-district-content');
    const overlay = document.getElementById('overlay');

    if (modalDistrict && overlay) {
        modalDistrict.style.display = 'flex';
        overlay.classList.add('active');

        setTimeout(() => {
            modalDistrict.classList.remove('hidden-modal-district');
            modalDistrict.classList.add('show-modal-district');
        }, 10);
    }
}

function hideModal() {
    const modalDistrict = document.getElementById('modal-district-content');
    const overlay = document.getElementById('overlay');

    if (modalDistrict && overlay) {
        modalDistrict.classList.remove('show-modal-district');
        modalDistrict.classList.add('hidden-modal-district');

        setTimeout(() => {
            modalDistrict.style.display = 'none';
            overlay.classList.remove('active');
        }, 450);
    }
}

function showError(input, message) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = message;
        formControl.className = 'form-input-modal error'; 
    } else {
        console.error("Error span with id='is-invalid' not found in parent element");
    }
}

function clearError(input) {
    const formControl = input.parentElement; 
    const errorSpan = formControl.parentElement.querySelector('#is-invalid'); 
    if (errorSpan) {
        errorSpan.innerText = ''; 
        formControl.className = 'form-input-modal'; 
    }
}