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

    if (checkbox1 && input_checkbox1) {
        checkbox1.addEventListener('change', function() {
            if (this.checked) {
                input_checkbox1.style.display = 'flex';
                requestAnimationFrame(() => {
                    input_checkbox1.classList.add('visible-input');
                });
            } else {
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

    // загрузка модального окна
    modalButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = button.getAttribute('data-modal');
            const modalElem = document.querySelector(`.modal[data-modal="${modalId}"]`);

            modalElem.classList.add('active');
            overlay.classList.add('active');
            body.style.position = 'fixed'; // Устанавливаем фиксированное позиционирование
            body.style.width = '100%'; // Убираем полосу прокрутки
        });
    });

    closeButton.addEventListener('click', closeModal);
    overlay.addEventListener('click', closeModal);
    
    // Обработчик нажатия клавиши Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });

    // обработка кнопки закрытии модального окна
    function closeModal() {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            activeModal.classList.remove('active');
            overlay.classList.remove('active');
            body.style.position = ''; // Возвращаем исходное позиционирование
            body.style.width = ''; // Возвращаем ширину
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
const wrapperOrder = document.getElementById('order-wrapper');
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
    const regex = /^(?:№|номер)\s+(.+)$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть № дела');
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
    const regex = /^(?:\d|[1-9]\d)\.(?:\d|[1-9]\d).(?:\d|[1-9]\d)\s*УК$/;
    if (input.value === '') {
        showError(input, 'Поле не может быть пустым');
        return false;
    } else if (!regex.test(input.value)) {
        showError(input, 'Неверный формат. Должен быть x.x, xx.x, x.xx или xx.xx УК.');
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

function addValidationListeners() {
    param1.addEventListener('input', validateParam1);
    param2.addEventListener('input', validateParam2);
    param3.addEventListener('input', validateParam3);
    param4.addEventListener('input', validateParam4);
    case_input.addEventListener('input', validateCaseinput);
    arrest_time.addEventListener('input', validateArrestTime);
}

function removeValidationListeners() {
    param1.removeEventListener('input', validateParam1);
    param2.removeEventListener('input', validateParam2);
    param3.removeEventListener('input', validateParam3);
    param4.removeEventListener('input', validateParam4);
    case_input.removeEventListener('input', validateCaseinput);
    arrest_time.removeEventListener('input', validateArrestTime);
}

function validateCaseinput() {
    ValidFormResolutionCaseInput(case_input);
}

function validateArrestTime() {
    ValidFormResolutionArrestTime(arrest_time);
}

function validateParam1() {
    ValidFormOrgan_param1(param1);
}

function validateParam2() {
    ValidFormOrgan_param2(param2);
}

function validateParam3() {
    ValidFormOrgan_param3(param3);
}

function validateParam4() {
    ValidFormOrgan_param4(param4);
}

function validateParam5() {
    ValidFormOrgan_param5(param5);
}

function validateParam6() {
    ValidFormOrgan_param6(param6);
}

function validateParam7() {
    ValidFormOrgan_param7(param7);
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

    let selectedWrapper;
    if (label === 'Ордер') {
        selectedWrapper = wrapperOrder;
        contanier_wrapper = contanier_order;
        wrapperOrder.classList.add('hidden-wrapper');

        enableFields([param1, param2, param3, param4, param5, param6, param7]);
        disableFields([case_input, arrest_time]);
    } else if (label === 'Постановление') {
        selectedWrapper = wrapperResolution;
        contanier_wrapper = contanier_res;
        wrapperResolution.classList.add('hidden-wrapper');
        disableFields([param1, param2, param3, param4, param5, param6, param7]);

    } else if (label === 'Повестка') {
        selectedWrapper = wrapperAgenda;
        contanier_wrapper = contanier_agenda
        wrapperAgenda.classList.add('hidden-wrapper');
        enableFields([param5, param6, param7]);
        disableFields([param1, param2, param3, param4, case_input, arrest_time]);
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

function disableFields(fields) {
    fields.forEach(field => {
        field.setAttribute('disabled', 'true');
        field.removeAttribute('required'); 
    });
}

function enableFields(fields) {
    fields.forEach(field => {
        field.removeAttribute('disabled');
        field.setAttribute('required', 'true'); 
    });
}


formBtn.addEventListener('click', function(event) {
    if (wrapperOrder.classList.contains('hidden-wrapper') && 
        (!ValidFormOrgan_param1(param1) || !ValidFormOrgan_param2(param2) || 
         !ValidFormOrgan_param3(param3) || !ValidFormOrgan_param4(param4))) {
        event.preventDefault();
        return;
    }

    if (wrapperResolution.classList.contains('hidden-wrapper')) {
        if (case_input.offsetParent === null) {
            case_input.removeAttribute('required');
        } else {
            case_input.setAttribute('required', 'true');
        }
        
        if (arrest_time.offsetParent === null) {
            arrest_time.removeAttribute('required');
        } else {
            arrest_time.setAttribute('required', 'true');
        }
        
        if(!ValidFormResolutionCaseInput(case_input) || !ValidFormResolutionArrestTime(arrest_time)) {
            event.preventDefault();
            return;
        }
    }

    if (wrapperAgenda.classList.contains('hidden-wrapper')) {
    }
});


document.addEventListener('DOMContentLoaded', function () {
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
});
