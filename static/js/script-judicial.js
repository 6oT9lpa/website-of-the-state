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
    function initializeModalEvent() {
        const modalDistrict = document.getElementById('modal-district-content');
        const createButton = document.getElementById('create-btn-district');
        const closeModalBtn = document.getElementById('btn-modal-close');
        const defendant = document.getElementById('defendant');
        const phone = document.getElementById('phone');
        const card = document.getElementById('card');
        const lawyer = document.getElementById('lawyer');
        const claim = document.getElementById('claim');
        const accessMessage = document.querySelector('#access-message');
        const closeButton = document.querySelector('.modal-close-error');

        document.addEventListener('click', function(event) {
            const dropdownBtn = document.querySelector('#dropdown-btn-0');
            const dropdownMenu = document.querySelector('#dropdown-0');
        
            if (event.target && event.target === dropdownBtn) {
                event.preventDefault();
                dropdownMenu.classList.toggle('open');
                dropdownBtn.classList.toggle('active');
            }
        
        });

        document.addEventListener('click', function(event) {
            const dropdown = document.querySelector('#dropdown-0');
            const dropdownButton = document.querySelector('#dropdown-btn-0');

            if (event.target && event.target.closest('#dropdown-menu-0')) {
                if (event.target.tagName === 'A') {
                    event.preventDefault();
                    const action = event.target.dataset.action;
                    dropdownButton.textContent = event.target.textContent;
                    document.getElementById('action-0').value = action;
                    dropdown.classList.remove('open');
                    dropdownButton.classList.remove('active');
                    updateContentProsecutor('action-0');
                }
            } else if (!event.target.closest('.dropdown')) {
                dropdown.classList.remove('open');
                dropdownButton.classList.remove('active');
            }
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

        function showAccessMessage() {
            if (accessMessage) {
                accessMessage.classList.add('hidden'); 

                setTimeout(() => {
                    accessMessage.style.display = 'block';
                    accessMessage.style.transform = 'translateY(30px)';

                    setTimeout(() => {
                        accessMessage.style.transform = 'translateY(0px)';
                        accessMessage.classList.add('show');
                        accessMessage.classList.remove('hidden');
                    }, 10);
                }, 200); 
            }
        }
        function closeModalError() {
            if (accessMessage) {
                accessMessage.classList.remove('show');
                accessMessage.style.transform = 'translateY(-30px)';
                accessMessage.classList.add('hidden');

                setTimeout(() => {
                    accessMessage.style.display = 'none'; 
                }, 500); 
            }
        }

        createButton?.addEventListener('click', showAccessMessage);
        closeButton?.addEventListener('click', closeModalError);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeModalError();
            }
        });

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

        const ModalValidationListeners = {
            defendant: (event) => validateDefendantForm(event.target),
            phone: (event) => validatePhoneForm(event.target),
            lawyer: (event) => validateLawyerForm(event.target),
            card: (event) => validateCardForm(event.target),
            claim: (event) => validateClaimForm(event.target)
        };
        
        function addModalValidationListener(field) {
            const listener = ModalValidationListeners[field.id];
            if (listener) {
                field.addEventListener('input', listener);
            }
        }
        
        function removeModalValidationListener(field) {
            const listener = ModalValidationListeners[field.id];
            if (listener) {
                field.removeEventListener('input', listener);
            }
        }        

        function enableModalFields(fields) {
            fields.forEach(field => {
                if (field) {
                    field.removeAttribute('disabled');
                    field.setAttribute('required', 'true');
                    addModalValidationListener(field); 
                }
            });
        }
        
        function disableModalFields(fields) {
            fields.forEach(field => {
                if (field) { 
                    field.value = '';
                    clearError(field);
                    field.setAttribute('disabled', 'true');
                    field.removeAttribute('required');
                    removeModalValidationListener(field); 
                }
            });
        }        

        function validateClaimForm(input) {
            if (!input || input.value.trim() === '') { 
                showError(input, 'Поле не может быть пустым');
                return false;
            }

            clearError(input);
            return true;
        }
        
        function validateDefendantForm(input) {
            if (!input || input.value.trim() === '') {
                showError(input, 'Поле не может быть пустым');
                return false;
            }
            
            const pattern = /^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$/;
            const value = input.value.trim();
        
            if (!pattern.test(value)) {
                showError(input, 'Введите данные в формате "Nick Name static"');
                return false;
            }

            clearError(input);
            return true;
        }

        function validateLawyerForm(input) {
            
            const pattern = /^[A-Z][a-z]+ [A-Z][a-z]+ \d{1,7}$/;
            const value = input.value.trim();
        
            if (value.trim() && !pattern.test(value)) {
                showError(input, 'Введите данные в формате "Nick Name static"');
                return false;
            }

            clearError(input);
            return true;
        }

        function validatePhoneForm(input) {
            if (!input || input.value.trim() === '') { 
                showError(input, 'Поле не может быть пустым');
                return false;
            }

            clearError(input);
            return true;
        }

        function validateCardForm(input) {
            if (!input || input.value.trim() === '') { 
                showError(input, 'Поле не может быть пустым');
                return false;
            }

            clearError(input);
            return true;
        }

        if (createButton && modalDistrict) {
            document.addEventListener('click', function(event) {
                if (event.target && event.target.id === 'create-btn-district') {
                    event.preventDefault();
                    showModal();
                }
            
                if (event.target && event.target.id === 'btn-modal-close') {
                    event.preventDefault();
                    hideModal();
                }
            });
            
            function showModal() {
                const modalDistrict = document.getElementById('modal-district-content');
                const overlay = document.getElementById('overlay');
            
                if (modalDistrict && overlay) {
                    modalDistrict.style.display = 'flex';
                    overlay.classList.add('active');
            
                    enableModalFields([defendant, phone, lawyer, card, claim]);
            
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

            document.addEventListener("click", function (e) {
                if (e.target && e.target.id === 'addDefenda-criminal') {
                    e.preventDefault();
                    handleAddDefenda('criminal-group-defenda', 'btn-add-defenda-criminal');
                }
            
                if (e.target && e.target.id === 'btn-add-defenda-criminal') {
                    e.preventDefault();
                    handleRemoveDefenda('criminal-group-defenda', 'btn-add-defenda-criminal');
                }
            
                if (e.target && e.target.id === 'addDefenda-complaint') {
                    e.preventDefault();
                    handleAddDefenda('complaint-group-defenda', 'btn-add-defenda-complaint');
                }
            
                if (e.target && e.target.id === 'btn-add-defenda-complaint') {
                    e.preventDefault();
                    handleRemoveDefenda('complaint-group-defenda', 'btn-add-defenda-complaint');
                }
            });
            
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

            let claimCounter = 1;
            document.addEventListener("click", function(e) {
                if (e.target && e.target.id === 'addClaim') {
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

                    enableModalFields([newInput]);

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

                if (e.target && e.target.id === 'btn-add-claim') {
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
            });

            
        } else {
            setTimeout(initializeModalEvent, 100); 
        }
    
    }

    initializeModalEvent();

});
