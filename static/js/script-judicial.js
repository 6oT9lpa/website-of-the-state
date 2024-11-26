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
            createButton.addEventListener('click', showModal);
            closeModalBtn.addEventListener('click', hideModal)
            
            function showModal() {
                modalDistrict.style.display = 'flex';
                document.querySelectorAll('#overlay').forEach(o => {
                    o.classList.add('active');
                });

                enableModalFields([defendant, phone, lawyer, card, claim])
                
                setTimeout(() => {
                    modalDistrict.classList.remove('hidden-modal-district')
                    modalDistrict.classList.add('show-modal-district')
                }, 10)
            }

            function hideModal() {
                modalDistrict.classList.remove('show-modal-district')
                modalDistrict.classList.add('hidden-modal-district')

                setTimeout(() => {
                    modalDistrict.style.display = 'none';
                    document.querySelectorAll('#overlay').forEach(o => {
                        o.classList.remove('active');
                    });
                }, 450);
            }

            let counter = 1; 
            const addDefendaButton = document.getElementById("addDefenda");
            const btnGroupDefenda = document.querySelector(".btn-group-defenda");
            const groupDefendaDiv = document.querySelector('.group-defenda');

            const deleteButton = document.createElement("a");
            deleteButton.classList.add("btn-add-defenda");
            deleteButton.textContent = "Удалить";
            deleteButton.style.display = "none"; 

            deleteButton.addEventListener("click", function(e) {
                e.preventDefault();
                const lastInputDiv = document.querySelector(".content-defenda:last-of-type");
                if (lastInputDiv) {
                    lastInputDiv.remove();
                    counter--; 
                    if (counter === 1) {
                        deleteButton.style.display = "none"; 
                        groupDefendaDiv.classList.remove('active-grid');
                    }
                }
            });
            btnGroupDefenda.appendChild(deleteButton);

            addDefendaButton.addEventListener("click", function(e) {
                groupDefendaDiv.classList.add('active-grid');

                const newContentDiv = document.createElement("div");
                newContentDiv.classList.add("content-defenda");

                const newLabel = document.createElement("label");
                newLabel.setAttribute("for", `defenda_${counter}`);
                newLabel.textContent = "Ответчик.";

                const newFormInputDiv = document.createElement("div");
                newFormInputDiv.classList.add("form-input-modal");
                newFormInputDiv.id = `defendant-input-${counter}`;

                const newInput = document.createElement("input");
                newInput.type = "text";
                newInput.id = `defendant`;
                newInput.name = "defenda[]";
                newInput.placeholder = "Введите ник";

                enableModalFields([newInput]);

                newFormInputDiv.appendChild(newInput);

                const newSpan = document.createElement("span");
                newSpan.classList.add("text-danger");
                newSpan.id = 'is-invalid';

                newContentDiv.appendChild(newLabel);
                newContentDiv.appendChild(newFormInputDiv);
                newContentDiv.appendChild(newSpan);

                const groupDefenda = document.querySelector(".group-defenda");
                groupDefenda.appendChild(newContentDiv);

                counter++;

                if (counter > 1) {
                    deleteButton.style.display = "inline-block";
                }
            });


            let claimCounter = 1;

            const addClaimButton = document.getElementById("addClaim");
            const btnGroupClaim = document.querySelector(".btn-group-claim");
            const groupClaimDiv = document.querySelector('.group-claim');
        
            const deleteClaimButton = document.createElement("a");
            deleteClaimButton.classList.add("btn-add-defenda");
            deleteClaimButton.textContent = "Удалить";
            deleteClaimButton.style.display = "none"; 

            deleteClaimButton.addEventListener("click", function(e) {
                e.preventDefault();
                const lastClaimDiv = document.querySelector(".content-claim:last-of-type");
                if (lastClaimDiv) {
                    lastClaimDiv.remove();
                    claimCounter--;
                    if (claimCounter <= 1) {
                        deleteClaimButton.style.display = "none"; 
                        groupClaimDiv.classList.remove('active-grid');
                    }
                }
            });
            btnGroupClaim.appendChild(deleteClaimButton);
        
            addClaimButton.addEventListener("click", function(e) {
                e.preventDefault();
                
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

                enableModalFields([newInput])
        
                newFormInputDiv.appendChild(newInput);

                const newSpan = document.createElement("span");
                newSpan.classList.add("text-danger");
                newSpan.id = `is-invalid`;

                newClaimDiv.appendChild(newLabel);
                newClaimDiv.appendChild(newFormInputDiv);
                newClaimDiv.appendChild(newSpan);

                const groupClaim = document.querySelector(".group-claim");
                groupClaim.appendChild(newClaimDiv);

                claimCounter++;
        
                if (claimCounter > 1) {
                    deleteClaimButton.style.display = "inline-block";
                }
            });

            
        } else {
            setTimeout(initializeModalEvent, 100); 
        }
    
    }

    initializeModalEvent();

});
