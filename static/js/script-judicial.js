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

        if (createButton && modalDistrict) {
            createButton.addEventListener('click', showModal);
            closeModalBtn.addEventListener('click', hideModal)
            
            function showModal() {
                modalDistrict.style.display = 'flex';
                document.querySelectorAll('#overlay').forEach(o => {
                    o.classList.add('active');
                });
                
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
                        groupDefendaDiv.classList.remove('active-grid')
                    }
                }
                });
            btnGroupDefenda.appendChild(deleteButton);

            addDefendaButton.parentElement.appendChild(deleteButton);
            addDefendaButton.addEventListener("click", function(e) {
                groupDefendaDiv.classList.add('active-grid')

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
                newInput.id = `defenda_${counter}`;
                newInput.name = "defenda[]";
                newInput.placeholder = "Введите ник";

                newFormInputDiv.appendChild(newInput);

                const newSpan = document.createElement("span");
                newSpan.classList.add("text-danger");
                newSpan.id = `defendant-invalid-${counter}`;

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
                newInput.id = `claims_${claimCounter}`;
                newInput.name = "claims[]";
                newInput.placeholder = "Введите требование";
        
                newFormInputDiv.appendChild(newInput);

                const newSpan = document.createElement("span");
                newSpan.classList.add("text-danger");
                newSpan.id = `claim-invalid-${claimCounter}`;

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
