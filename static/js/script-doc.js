const judicialOfficeButton = document.getElementById('load-judicial-office');
const prosecutionOfficeButton = document.getElementById('load-prosecution-office');
const backButton = document.createElement('a');
backButton.textContent = 'Назад';
backButton.classList.add('nav-button', 'back-button');
backButton.style.display = 'none';
const supremeButton = document.getElementById('load-claim-supreme');
const districtButton = document.getElementById('load-claim-district');
const judicialContent = document.getElementById('judicial-content');
const attorneyContent = document.getElementById('attorney-content');

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
    } else if (state === 'showProsecutionOffice') {
        showProsecutionOffice();
    } else {
        attorneyContent.innerHTML = '';
        attorneyContent.classList.remove('fade-in');
        [supremeButton, districtButton, documentsProsecutorButton, applicationsProsecutorButton].forEach(button => {
            button.classList.remove('active-button');
        });
    }
}

const documentsProsecutorButton = document.getElementById('load-documents-prosecutor');
const applicationsProsecutorButton = document.getElementById('load-applications-prosecutor');

function showProsecutionOffice() {
    prosecutionOfficeButton.classList.remove('fade-in-nav');
    judicialOfficeButton.classList.remove('fade-in-nav');

    prosecutionOfficeButton.classList.add('hidden-nav');
    judicialOfficeButton.classList.add('hidden-nav');

    prosecutionOfficeButton.style.transform = 'translateX(300px)';
    judicialOfficeButton.style.transform = 'translateX(-300px)';
    setTimeout(() => { 
        prosecutionOfficeButton.style.display = 'none';
        judicialOfficeButton.style.display = 'none';
    }, 300);

    setTimeout(() => {
        documentsProsecutorButton.style.display = 'inline-flex';
        applicationsProsecutorButton.style.display = 'inline-flex';

        setTimeout(() => {
            documentsProsecutorButton.style.transform = 'translateX(0px)';
            applicationsProsecutorButton.style.transform = 'translateX(0px)';

            documentsProsecutorButton.classList.remove('hidden-nav');
            documentsProsecutorButton.classList.add('fade-in-nav'); 
            applicationsProsecutorButton.classList.remove('hidden-nav');
            applicationsProsecutorButton.classList.add('fade-in-nav');
            backButton.classList.add('nav-button');
            backButton.style.display = 'inline-flex';
        }, 300);
    }, 300);
}

backButton.addEventListener('click', () => {
    localStorage.removeItem('officeState');
    sessionStorage.removeItem('selectedButton');
    sessionStorage.removeItem('selectedUrl');

    [supremeButton, districtButton].forEach(button => {
        button.classList.remove('active-button');
    });
    
    attorneyContent.innerHTML = '';
    attorneyContent.classList.remove('fade-in');
    districtButton.style.transform = 'translateX(300px)';
    supremeButton.style.transform = 'translateX(-300px)';

    districtButton.classList.add('hidden-nav');
    districtButton.classList.remove('fade-in-nav'); 
    supremeButton.classList.add('hidden-nav');
    supremeButton.classList.remove('fade-in-nav');
    backButton.classList.remove('nav-button');
    backButton.style.display = 'none';

    setTimeout(() => {
        districtButton.style.display = 'none';
        supremeButton.style.display = 'none';
    }, 300);

    setTimeout(() => {
        prosecutionOfficeButton.style.display = 'inline-flex';
        judicialOfficeButton.style.display = 'inline-flex';
        setTimeout(() => { 
            prosecutionOfficeButton.classList.add('fade-in-nav');
            judicialOfficeButton.classList.add('fade-in-nav');
            
            prosecutionOfficeButton.classList.remove('hidden-nav');
            judicialOfficeButton.classList.remove('hidden-nav');

            prosecutionOfficeButton.style.transform = 'translateX(0px)';
            judicialOfficeButton.style.transform = 'translateX(0px)';
        }, 30);   
    }, 300);
});

prosecutionOfficeButton.addEventListener('click', () => {
    saveState('showProsecutionOffice');
    showProsecutionOffice();
});

documentsProsecutorButton.addEventListener('click', function (event) {
    event.preventDefault();
    toggleContent('load-documents-prosecutor', '/get-documet-prosecutor-content');
});

applicationsProsecutorButton.addEventListener('click', function (event) {
    event.preventDefault();
    toggleContent('load-applications-prosecutor', '/get-application-prosecutor-content');
});

function showJudicialOffice() {
    prosecutionOfficeButton.classList.remove('fade-in-nav');
    judicialOfficeButton.classList.remove('fade-in-nav');
    
    prosecutionOfficeButton.classList.add('hidden-nav');
    judicialOfficeButton.classList.add('hidden-nav');
    
    prosecutionOfficeButton.style.transform = 'translateX(300px)';
    judicialOfficeButton.style.transform = 'translateX(-300px)';
    setTimeout(() => { 
        prosecutionOfficeButton.style.display = 'none';
        judicialOfficeButton.style.display = 'none';
    }, 300);

    setTimeout(() => {
        districtButton.style.display = 'inline-flex';
        supremeButton.style.display = 'inline-flex';

        setTimeout(() => {
            districtButton.style.transform = 'translateX(0px)';
            supremeButton.style.transform = 'translateX(0px)';

            districtButton.classList.remove('hidden-nav');
            districtButton.classList.add('fade-in-nav'); 
            supremeButton.classList.remove('hidden-nav');
            supremeButton.classList.add('fade-in-nav');
            backButton.classList.add('nav-button');
            backButton.style.display = 'inline-flex';
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

    [supremeButton, districtButton, documentsProsecutorButton, applicationsProsecutorButton].forEach(button => {
        button.classList.remove('active-button');
    });

    attorneyContent.innerHTML = '';
    attorneyContent.classList.remove('fade-in');

    documentsProsecutorButton.style.transform = 'translateX(300px)';
    applicationsProsecutorButton.style.transform = 'translateX(-300px)';

    documentsProsecutorButton.classList.add('hidden-nav');
    documentsProsecutorButton.classList.remove('fade-in-nav');
    applicationsProsecutorButton.classList.add('hidden-nav');
    applicationsProsecutorButton.classList.remove('fade-in-nav');

    backButton.classList.remove('nav-button');
    backButton.style.display = 'none';

    setTimeout(() => {
        documentsProsecutorButton.style.display = 'none';
        applicationsProsecutorButton.style.display = 'none';
    }, 300);

    setTimeout(() => {
        prosecutionOfficeButton.style.display = 'inline-flex';
        judicialOfficeButton.style.display = 'inline-flex';

        setTimeout(() => {
            prosecutionOfficeButton.classList.add('fade-in-nav');
            judicialOfficeButton.classList.add('fade-in-nav');

            prosecutionOfficeButton.classList.remove('hidden-nav');
            judicialOfficeButton.classList.remove('hidden-nav');

            prosecutionOfficeButton.style.transform = 'translateX(0px)';
            judicialOfficeButton.style.transform = 'translateX(0px)';
        }, 15);
    }, 300);
});


function toggleContent(buttonId, url) {
    sessionStorage.setItem('selectedButton', buttonId);
    sessionStorage.setItem('selectedUrl', url);

    [supremeButton, districtButton, documentsProsecutorButton, applicationsProsecutorButton].forEach(button => {
        button.classList.remove('active-button');
    });

    [attorneyContent, judicialContent].forEach(content => {
        content.innerHTML = '';
        content.classList.remove('fade-in');
    })

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


const showElement = (element) => {
    element.style.display = 'block';
    element.style.transform = 'translateX(20px)';
    setTimeout(() => {
        element.classList.add('fade-in');
        element.style.transform = 'translateX(0px)';
        element.classList.remove('hidden-input');
    }, 10);
};

const hideElement = (element) => {
    element.classList.remove('fade-in');
    element.style.transform = 'translateX(-20px)';
    element.classList.add('hidden-input');
    setTimeout(() => {
        element.style.display = 'none'
    }, 300);
};

document.addEventListener('DOMContentLoaded', function() {
    const checkbox1 = document.getElementById('param1_checkbox');
    const checkbox2 = document.getElementById('param2_checkbox');
    const input_checkbox1 = document.getElementById('input_checkbox1');
    const input_checkbox2 = document.querySelectorAll('#input_checkbox2');
    const caseInput = document.getElementById('caseInput');

    if (checkbox1 && input_checkbox1) {
        checkbox1.addEventListener('change', function() {
            if (this.checked) {
                enableFields([caseInput]);
                showElement(input_checkbox1)
            } else {
                disableFields([caseInput]);
                hideElement(input_checkbox1)
            }
        });
    }

    if (checkbox2 && input_checkbox2) {
        checkbox2.addEventListener('change', function() {
            if (this.checked) {
                enableFields([arrest_time, param2_nickname]);
                input_checkbox2.forEach(i => showElement(i));
            } else {
                disableFields([arrest_time, param2_nickname]);
                input_checkbox2.forEach(i => hideElement(i));
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            hideModal(document.querySelector('#modal-creater'));
        }
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

    if (isAuthenticated && isPermission) {
        document.getElementById('open-modal-creater').addEventListener('click', function(event) {
            event.preventDefault();
            showModal(document.querySelector('#modal-creater'));
        })
        document.getElementById('close-modal-creater').addEventListener('click', function(event) {
            event.preventDefault();
            hideModal(document.querySelector('#modal-creater'));
        })
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
            dropdownBtn.textContent = e.target.textContent;
            document.getElementById(hiddenInputId).value = action;
            dropdown.classList.remove('open');
            dropdownBtn.classList.remove('active');
            console.log(document.querySelector('#action-1').value);

            selectOption(document.querySelector('#action-1').value) 
        });
    }
    setupDropdown(document.querySelector('#dropdown-1'), document.querySelector('#dropdown-btn-1'), document.querySelector('#dropdown-menu-1'), 'action-1');

}); 

function toggleOptions() {
    const options = document.getElementById("options");
    options.classList.toggle("hidden");

    if (options.style.display === "block") {
        options.style.display = "none";
        options.style.opacity = "0";
    } else {
        options.style.display = "block";
        setTimeout(() => {
            options.style.opacity = "1";
        }, 100);
    }
}

const param1 = document.getElementById('param1');
const param2 = document.getElementById('param2');
const param3 = document.getElementById('param3');
const param4 = document.getElementById('param4');
const param5 = document.getElementById('param5');
const param6 = document.getElementById('param6');
const param7 = document.getElementById('param7');
const param2_nickname = document.getElementById('param2_nickname');
const typeOrder = document.getElementById('typeOrder');
const input_degreeRI = document.getElementById('degreeRI');
const input_applicationNum = document.getElementById('applicationNum');
const input_nameCrimeOrgan = document.getElementById('nameCrimeOrgan');
const input_adreasCrimeOrgan = document.getElementById('adreasCrimeOrgan');
const termImprisonment = document.getElementById('termImprisonment');
const formBtn = document.getElementById('btn');
const case_input = document.getElementById('caseInput');
const arrest_time = document.getElementById('arrest_time');

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

function VaidateFormParam2Nickname(input) {
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormResolutionCaseInput(input) {
    if (!document.getElementById('param1_checkbox').checked) {
        return true; 
    }
    const regex = /^JD-+(.+)$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть JD-номер');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormResolutionArrestTime(input) {
    if (input.offsetParent === null) {
        return true; 
    }
    const datePattern = /^(?:\d{4}[-./\\\s]{1,}\d{2}[-./\\\s]{1,}\d{2})$/;
    const timePattern = /^\d{2}:\d{2}$/;

    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!(datePattern.test(input.value.split(' ')[0]) && timePattern.test(input.value.split(' ')[1]))) {
        showError(input, 'Неверный формат. Должен быть год месяц день час:минута');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param1(input) {
    const regex = /^(?:\d{1,2}(?:\.\d{1,2}){0,2}\s*(?:УК|АК))(?:,\s*\d{1,2}(?:\.\d{1,2}){0,2}\s*(?:УК|АК))*$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть x.x УК, xx.x УК, x.xx УК, xx.xx УК или x.x.x УК, разделенные запятыми.');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param2(input) {
    const regex = /^(?:\d|[1-9]\d)\s*лет$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть x лет.');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param3(input) {
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param4(input) {
    const regex = /^(?:Прокуратура|FIB|USSS|Министерство\sЮстиций)\s+(?:№|номер)\s+(.+)$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть Организация № дела');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param5(input)
{
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param6(input)
{
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidFormOrgan_param7(input)
{
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidateInputDegreeRI(input)
{
    if (input.value !== '')
    {
        clearError(input);

        if (input.value === 'полностью'){
            clearError(input);
            return true;
        }
        else if (input.value === 'частично'){
            clearError(input);
            return true;
        }
        else{
            showError(input, 'Неприкос можно снять *частично* либо *полностью*');
        }
    }
    else
    {
        showError(input, 'Поле не может быть пустым');
        return false;
    }
}

function ValidateInputApplicationNum(input) {
    const regex = /^(Иск|Прокуратура)\s№\s*\d+$/;
    
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Введите "Иск № номер" или "Прокуратура № номер".');
        return false;
    } else {
        clearError(input);
        return true;
    }
}

function ValidateNameCrimeOrgan(input)
{
    if (input.value === '')
    {
        showError(input, 'Поле не может быть пустым');
        return false;
    }
    else {
        clearError(input);
        return false;
    }
}

function ValidateAdreasCrimeOrgan(input)
{
    if (input.value === '')
        {
            showError(input, 'Поле не может быть пустым');
            return false;
        }
        else {
            clearError(input);
            return false;
        }
}

function ValidFormTypeOrder(input) {
    if (input.value !== '') {
        clearError(input);

        const articlesAccusation = document.getElementById('articlesAccusation');
        const degreeRI = document.getElementById('degree_ri');
        const applicationNum = document.getElementById('application_num');
        const number_offWork = document.getElementById('number_offWork');
        const termImprisonment = document.getElementById('termImprisonment');
        const labelTime = document.getElementById('label-time');
        const time = document.getElementById('time');
        const carBrand = document.getElementById('carBrand');
        const adreasSuspect = document.getElementById('adreasSuspect');
        const nameOrganForOrder = document.getElementById('nameOrganForOrder');
        const adreasOrganForOrder = document.getElementById('adreasOrganForOrder');

        const elements = [
            articlesAccusation, degreeRI, applicationNum, number_offWork,
            termImprisonment, nameOrganForOrder, time, adreasOrganForOrder,
            adreasSuspect, carBrand
        ];
        
        elements.forEach(element => hideElement(element));
        disableFields([input_degreeRI, input_applicationNum, param1, param2, param3, param4]);

        switch (input.value) {
            case 'SA':
            case 'Search Access':
                clearError(input);

                setTimeout(() => {
                    enableFields([param3, param1])

                    showElement(time);
                    showElement(articlesAccusation);
                    showElement(carBrand);
                    showElement(adreasSuspect);

                    labelTime.textContent = 'Срок исполнения';
                }, 310);

                return true;

            case 'AS':
            case 'Arrest and Search':
                clearError(input);

                setTimeout(() => {
                    enableFields([param1, param2, param3, param4])

                    showElement(time);
                    showElement(termImprisonment);
                    showElement(number_offWork);
                    showElement(articlesAccusation);

                    labelTime.textContent = 'Срок исполнения';
                }, 310);
                return true;

            case 'ML':
            case 'Martial Law':
                clearError(input);
                return true;

            case 'AR':
            case 'Access To Raid':
                clearError(input);    

                setTimeout(() => {
                    enableFields([param3, param4, param1, input_adreasCrimeOrgan, input_nameCrimeOrgan])

                    showElement(articlesAccusation);
                    showElement(number_offWork);
                    showElement(nameOrganForOrder);
                    showElement(time);
                    showElement(adreasOrganForOrder);

                    labelTime.textContent = 'Срок исполнения';
                }, 310);
                return true;

            case 'RI':
            case 'Removal of Immunity':
                clearError(input);

                setTimeout(() => { 
                    enableFields([param3, input_degreeRI, input_applicationNum])

                    showElement(applicationNum);
                    showElement(degreeRI);
                    showElement(time);

                    labelTime.textContent = 'Срок действия';
                }, 310);
                return true;

            case 'FW':
            case 'Federal Wanted':
                clearError(input);

                setTimeout(() => {
                    enableFields([param3, param1, param4])

                    showElement(articlesAccusation);
                    showElement(number_offWork);
                    showElement(time);

                    labelTime.textContent = 'Срок действия';
                }, 310);

                return true;

            default:
                showError(input, 'Такого ордера не существует!');

                return false;
                
        }
    } else {
        showError(input, 'Поле не может быть пустым');
        return false;
    }
}

function enableFields(fields) {
    fields.forEach(field => {
        if (field) {
            field.removeAttribute('disabled');
            field.setAttribute('required', 'true');
            addValidationListener(field); 
        }
    });
}

function disableFields(fields) {
    fields.forEach(field => {
        if (field) { 
            field.value = '';
            clearError(field);
            field.setAttribute('disabled', 'true');
            field.removeAttribute('required');
            removeValidationListener(field); 
        }
    });
}

const validationListeners = {
    param1: () => ValidFormOrgan_param1(param1),
    param2: () => ValidFormOrgan_param2(param2),
    param3: () => ValidFormOrgan_param3(param3),
    param4: () => ValidFormOrgan_param4(param4),
    param5: () => ValidFormOrgan_param5(param5),
    param6: () => ValidFormOrgan_param6(param6),
    param7: () => ValidFormOrgan_param7(param7),
    param2_nickname: () => VaidateFormParam2Nickname(param2_nickname),
    caseInput: () => ValidFormResolutionCaseInput(case_input),
    arrest_time: () => ValidFormResolutionArrestTime(arrest_time),
    typeOrder: () => ValidFormTypeOrder(typeOrder),
    degreeRI: () => ValidateInputDegreeRI(input_degreeRI),
    applicationNum: () => ValidateInputApplicationNum(input_applicationNum),
    nameCrimeOrgan: () => ValidateNameCrimeOrgan(input_nameCrimeOrgan),
    adreasCrimeOrgan: () => ValidateAdreasCrimeOrgan(input_adreasCrimeOrgan)
};

function addValidationListener(field) {
    const listener = validationListeners[field.id];
    if (listener) {
        field.addEventListener('input', listener);
    }
}

function removeValidationListener(field) {
    const listener = validationListeners[field.id];

    if (listener) {
        field.removeEventListener('input', listener);
    }
}

const contanier_res = document.getElementById('contanier-wrapper_res');
const contanier_order = document.getElementById('contanier-wrapper_order');
const wrapperResolution = document.getElementById('resolution-wrapper');
const wrapperOrder = document.getElementById('order-wrapper');

function selectOption(label) {

    [wrapperOrder, wrapperResolution].forEach(wrapper => {
        wrapper.classList.remove('hidden-wrapper');
        wrapper.style.height = '0';
        wrapper.style.display = 'none';
    });

    [contanier_order, contanier_res].forEach(container => {
        container.style.height = '0';
        container.style.display = 'none';
    });

    disableFields([param2_nickname, typeOrder, case_input, arrest_time, param1, param2, param3, param4, param5, param6, param7, input_degreeRI, input_applicationNum, input_adreasCrimeOrgan, input_nameCrimeOrgan]);
    let selectedWrapper;
    let contanier_wrapper;
    switch(label){
        case 'Order':
            selectedWrapper = wrapperOrder;
            contanier_wrapper = contanier_order;
            wrapperOrder.classList.add('hidden-wrapper');

            contanier_order.style.display = 'block';
            contanier_order.style.height = 'auto';

            enableFields([typeOrder]);
            toggleCustomButton(false);
            break;
        
        case 'Resolution':
            selectedWrapper = wrapperResolution;
            contanier_wrapper = contanier_res;

            contanier_res.style.display = 'block';
            contanier_res.style.height = 'auto';

            wrapperResolution.classList.add('hidden-wrapper');
            toggleCustomButton(true);
            break;
    }        

    if (selectedWrapper) {
        selectedWrapper.style.display = 'block';
        selectedWrapper.style.height = selectedWrapper.scrollHeight + 'px'

        selectedWrapper.addEventListener('transitionend', function handler() {
            selectedWrapper.style.height = 'auto';
            contanier_wrapper.style.height = 'auto';
            selectedWrapper.removeEventListener('transitionend', handler);
        });
    }
}

const static = document.getElementById('static')
const checkbox1 = document.getElementById('param1_checkbox');
const checkbox2 = document.getElementById('param2_checkbox');

if (isAuthenticated && isPermission) {
    formBtn.addEventListener('click', function(event) {
        if (static.value === '' && !ValidFormTypeOrder(typeOrder)) {
            event.preventDefault();
            console.log('static', static);
            return;
        }

        let isValid = true;
        if (wrapperResolution.classList.contains('hidden-wrapper')) {
            if (!ValidFormResolutionCaseInput(case_input) && checkbox1.checked) { isValid = false; }
            if (!VaidateFormParam2Nickname(param2_nickname) && checkbox2.checked) { isValid = false; }
            if (!ValidFormResolutionArrestTime(arrest_time) && checkbox2.checked) { isValid = false; }
        }

        if (!isValid) {
            event.preventDefault();
        }

    });

    document.getElementById('resolutionForm').addEventListener('submit', function() {
        document.getElementById('btn').disabled = true;
        document.getElementById('loadingText').style.display = 'inline';
    });
}

const showElementButton = (element) => {
    element.style.display = 'flex';
    setTimeout(() => {
        element.classList.add('show-custom');
        element.classList.remove('hidden-custom');
    }, 10);
};

const hideElementButton = (element) => {
    element.classList.remove('show-custom');
    element.classList.add('hidden-custom');
    setTimeout(() => {
        element.style.display = 'none';
    }, 300);
};

function toggleCustomButton(show) {
    const customButton = document.getElementById('btn-custom-resolution');

    if (customButton) {
        if (show) {
            showElementButton(customButton);
            customButton.addEventListener('click', toggleCustomForm);
            document.querySelector('[name="custom_button_pressed"]').value = "false"
        } else {
            hideElementButton(customButton);
            customButton.removeEventListener('click', toggleCustomForm);     
        }
    }
    return false;
}

function toggleCustomForm() {
    document.querySelectorAll('.checkbox input[type="checkbox"]').forEach(checkbox => {
        checkbox.setAttribute('disabled', true);
        checkbox.closest('.checkbox-wrapper').style.display = 'none';
    });

    document.querySelector('[name="custom_button_pressed"]').value = "true"
    document.getElementById('custom-inputs-container').classList.remove('hidden');

    
}

let inputCount = 0;
const maxTextareaWidth = 300; 
const compactWidth = 180; 
const maxTextareaHeight = 100; 

function addInput() {
    if (inputCount >= 10) return;

    const newTextarea = document.createElement('textarea');
    newTextarea.name = `custom_text_${inputCount}`;
    newTextarea.className = 'fade-in-text'; 
    newTextarea.placeholder = 'Введите значение';

    newTextarea.rows = 1;
    newTextarea.oninput = () => autoResizeTextarea(newTextarea);
    newTextarea.onfocus = () => expandTextarea(newTextarea);
    newTextarea.onblur = () => shrinkTextarea(newTextarea);

    const container = document.createElement('div');
    container.className = 'form-textarea';
    container.appendChild(newTextarea);

    document.getElementById('dynamic-input-container').appendChild(container);
    inputCount++;

    setTimeout(() => {
        newTextarea.classList.remove('fade-in-text');
    }, 300); 
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto'; 
    textarea.style.height = Math.min(textarea.scrollHeight, maxTextareaHeight) + 'px';
    textarea.style.width = Math.min(textarea.scrollWidth + 15, maxTextareaWidth) + 'px';
}

function expandTextarea(textarea) {
    textarea.style.width = maxTextareaWidth + 'px'; 
    textarea.style.height = Math.min(textarea.scrollHeight, maxTextareaHeight) + 'px';
}

function shrinkTextarea(textarea) {
    textarea.style.width = compactWidth + 'px'; 
    textarea.style.height = 'auto'; 
    textarea.rows = 1; 
}

function resetCustomForm() {
    document.querySelectorAll('.checkbox input[type="checkbox"]').forEach(checkbox => {
        checkbox.removeAttribute('disabled');
        checkbox.closest('.checkbox-wrapper').style.display = 'flex';
    });

    document.getElementById('custom-inputs-container').classList.add('hidden');
    document.querySelector('[name="custom_button_pressed"]').value = "false"

    const inputContainer = document.getElementById('dynamic-input-container');
    while (inputContainer.children.length > 0) {
        inputContainer.removeChild(inputContainer.lastChild);
    }
    inputCount = 0;
}

