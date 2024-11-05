let bg = document.querySelector('.background');

// паралакс эффект на background
window.addEventListener('mousemove', function(e) {
    let x = e.clientX / window.innerWidth;
    let y = e.clientY / window.innerHeight;  
    bg.style.transform = 'translate(-' + x * 50 + 'px, -' + y * 50 + 'px)';
});

document.addEventListener('DOMContentLoaded', function() {
    const modalButtons = document.querySelectorAll('.modal-button');
    const closeButton = document.querySelector('.modal-close');
    const overlay = document.querySelector('.overlay');
    const body = document.body; 
    const checkbox1 = document.getElementById('param1_checkbox');
    const checkbox2 = document.getElementById('param2_checkbox');
    const input_checkbox1 = document.getElementById('input_checkbox1');
    const input_checkbox2 = document.getElementById('input_checkbox2');
    const caseInput = document.getElementById('caseInput');
    const access_message = document.querySelector('#access-message');

    document.getElementById('load-prosecution-office').addEventListener('click', function(event) {
        event.preventDefault();

        fetch('/get_prosecution_office_content')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка сети');
                }
                return response.text();
            })
            .then(data => {
                const attorneyContent = document.getElementById('attorney-content');
                if (attorneyContent) {
                    attorneyContent.innerHTML = data;
                    attorneyContent.classList.add('fade-in');
                    document.getElementById('load-prosecution-office').classList.add('active-button');
                } else {
                    console.error('Элемент с id "attorney-content" не найден.');
                }
            })
            .catch(error => console.error('Ошибка загрузки контента:', error));
    });

    if (checkbox1 && input_checkbox1) {
        checkbox1.addEventListener('change', function() {
            if (this.checked) {
                enableFields([caseInput]);
                input_checkbox1.style.display = 'flex';
                requestAnimationFrame(() => {
                    input_checkbox1.classList.add('visible-input');
                });
            } else {
                disableFields([caseInput]);
                input_checkbox1.classList.remove('visible-input');
                input_checkbox1.addEventListener('transitionend', function handleTransitionEnd() {
                    input_checkbox1.style.display = 'none'; 
                    input_checkbox1.removeEventListener('transitionend', handleTransitionEnd);
                }, { once: true });
            }
        });
    }

    if (checkbox2 && input_checkbox2) {
        checkbox2.addEventListener('change', function() {
            if (this.checked) {
                input_checkbox2.style.display = 'flex';
                requestAnimationFrame(() => {
                    input_checkbox2.classList.add('visible-input');
                });
            } else {
                input_checkbox2.classList.remove('visible-input');
                input_checkbox2.addEventListener('transitionend', function handleTransitionEnd() {
                    input_checkbox2.style.display = 'none'; 
                    input_checkbox2.removeEventListener('transitionend', handleTransitionEnd);
                }, { once: true });
            }
        });
    }
    
    modalButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = button.getAttribute('data-modal');
            const modalElem = document.querySelector(`.modal[data-modal="${modalId}"]`);
    
            if (isAuthenticated && isPermission) { 
                modalElem.classList.add('active');
                overlay.classList.add('active');
                body.style.position = 'fixed'; 
                body.style.width = '100%'; 
            }
            else{
                access_message.classList.add('hidden'); // Изначально скрываем
                access_message.style.display = 'block'; 
                access_message.style.transform = 'translateY(30px)';
                setTimeout(() => {
                    access_message.style.transform = 'translateY(0px)';
                    access_message.classList.add('show');
                    access_message.classList.remove('hidden'); // Убираем класс hidden после показа
                }, 10); 
            }
        });
    });

    if (isAuthenticated && isPermission) {
        closeButton.addEventListener('click', closeModal);
        overlay.addEventListener('click', closeModal);
    } 
    else{
        document.querySelector('.modal-close-error')?.addEventListener('click', closeModal_error);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeModal_error();
        }
    });

    function closeModal_error() {
        if (access_message) {
            access_message.classList.remove('show');
            access_message.style.transform = 'translateY(-30px)';
            access_message.classList.add('hidden');
            setTimeout(() => {
                access_message.style.display = 'none'; 
            }, 500); 
        }
    }

    function closeModal() {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            activeModal.classList.remove('active');
            overlay.classList.remove('active');
            body.style.position = ''; 
            body.style.width = '';
        }
    }
}); 

// анимации для option
function toggleOptions() {
    const options = document.getElementById("options");
    options.classList.toggle("hidden");

    if (options.style.display === "block") {
        options.style.display = "none";
        options.style.opacity = "0";
    } else {
        options.style.display = "block";
        setTimeout(() => {
            options.style.opacity = "1"; // Анимация появления
        }, 0);
    }
}

const param1 = document.getElementById('param1');
const param2 = document.getElementById('param2');
const param3 = document.getElementById('param3');
const param4 = document.getElementById('param4');
const param5 = document.getElementById('param5');
const param6 = document.getElementById('param6');
const param7 = document.getElementById('param7');
const typeOrder = document.getElementById('typeOrder');
const input_degreeRI = document.getElementById('degreeRI');
const input_applicationNum = document.getElementById('applicationNum');
const input_nameCrimeOrgan = document.getElementById('nameCrimeOrgan');
const input_adreasCrimeOrgan = document.getElementById('adreasCrimeOrgan');
const wrapperOrder = document.getElementById('order-wrapper');
const termImprisonment = document.getElementById('termImprisonment');
const wrapperResolution = document.getElementById('resolution-wrapper');
const wrapperAgenda = document.getElementById('agenda-wrapper');
const contanier_res = document.getElementById('contanier-wrapper_res');
const contanier_order = document.getElementById('contanier-wrapper_order');
const contanier_agenda = document.getElementById('contanier-wrapper_agenda');
const formBtn = document.getElementById('btn');
const case_input = document.getElementById('case');
const arrest_time = document.getElementById('arrest_time');

function showError(input, message) {
    const formControl = input.parentElement;
    formControl.className = 'form-input error';
    const errorSpan = formControl.querySelector('#is-unvalid');
    errorSpan.innerText = message;
}

function clearError(input) {
    const formControl = input.parentElement;
    formControl.className = 'form-input'; 
    const errorSpan = formControl.querySelector('#is-unvalid');
    if (errorSpan) {
        errorSpan.innerText = '';
    }
}

function ValidFormResolutionCaseInput(input) {
    if (input.offsetParent === null) {
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

        // Функция для добавления анимации появления
        const showElement = (element) => {
            element.style.display = 'block'
            element.style.transform = 'translateX(20px)';
            setTimeout(() => {
                element.classList.add('fade-in');
                element.style.transform = 'translateX(0px)';
                element.classList.remove('hidden-input');
            }, 10);
        };

        // Функция для добавления анимации исчезновения
        const hideElement = (element) => {
            element.classList.remove('fade-in');
            element.style.transform = 'translateX(-20px)';
            element.classList.add('hidden-input');
            setTimeout(() => {
                element.style.display = 'none'
            }, 300);
        };
        
        elements.forEach(element => hideElement(element));
        disableFields([input_degreeRI, input_applicationNum, param1, param2, param3, param4]);

        // Анимация в зависимости от типа ордера
        switch (input.value) {
            case 'SA':
            case 'Search Access':
                clearError(input);

                setTimeout(() => {
                    enableFields([param3])

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

function selectOption(label) {
    const selectedValue = document.getElementById('selected-value').getElementsByTagName('span')[0];

    [wrapperOrder, wrapperResolution, wrapperAgenda].forEach(wrapper => {
        wrapper.classList.remove('hidden-wrapper');
        wrapper.style.height = '0';
        wrapper.style.display = 'none';
    });

    [contanier_order, contanier_res, contanier_agenda].forEach(container => {
        container.style.height = '0';
        container.style.display = 'none';
    });

    selectedValue.textContent = label;
    toggleOptions();

    disableFields([typeOrder, case_input, arrest_time, param1, param2, param3, param4, param5, param6, param7, input_degreeRI, input_applicationNum, input_adreasCrimeOrgan, input_nameCrimeOrgan]);
    let selectedWrapper;
    if (label === 'Ордер') {
        selectedWrapper = wrapperOrder;
        contanier_wrapper = contanier_order;
        wrapperOrder.classList.add('hidden-wrapper');
        enableFields([typeOrder]);

    } else if (label === 'Постановление') {
        selectedWrapper = wrapperResolution;
        contanier_wrapper = contanier_res;
        wrapperResolution.classList.add('hidden-wrapper');
        disableFields([typeOrder, case_input, arrest_time, param1, param2, param3, param4, param5, param6, param7, input_degreeRI, input_applicationNum, input_adreasCrimeOrgan, input_nameCrimeOrgan]);

    } else if (label === 'Повестка') {
        selectedWrapper = wrapperAgenda;
        contanier_wrapper = contanier_agenda
        wrapperAgenda.classList.add('hidden-wrapper');
        enableFields([param5, param6, param7]);
        disableFields([typeOrder, case_input, arrest_time, param1, param2, param3, param4, param5, param6, param7, input_degreeRI, input_applicationNum, input_adreasCrimeOrgan, input_nameCrimeOrgan]);
    }

    if (selectedWrapper) {
        selectedWrapper.style.display = 'block';
        contanier_wrapper.style.display = 'flex';
        selectedWrapper.style.height = selectedWrapper.scrollHeight + 'px';
        contanier_wrapper.style.height = selectedWrapper.scrollHeight + 'px';

        selectedWrapper.addEventListener('transitionend', function handler() {
            selectedWrapper.style.height = 'auto';
            contanier_wrapper.style.height = 'auto';
            selectedWrapper.removeEventListener('transitionend', handler);
        });
    }
}

const static = document.getElementById('static')

if (isAuthenticated && isPermission) {
    formBtn.addEventListener('click', function(event) {
        if (static.value === '' && !ValidFormTypeOrder(typeOrder)) {
            event.preventDefault();
            return;
        }


        if (wrapperResolution.classList.contains('hidden-wrapper')) {
            document.getElementById('param1_checkbox').addEventListener('change', function () {
                const caseInput = document.getElementById('case');
                
            });
            
            document.getElementById('param2_checkbox').addEventListener('change', function () {
                const arrestTime = document.getElementById('arrest_time');
                if (this.checked) {
                    enableFields([arrestTime]);
                } else {
                    disableFields([arrestTime]);
                }
            });
            
            if(!ValidFormResolutionCaseInput(case_input) || !ValidFormResolutionArrestTime(arrest_time)) {
                event.preventDefault();
                return;
            }
        }

        if (wrapperAgenda.classList.contains('hidden-wrapper')) {
        }
    });
}
