document.addEventListener('DOMContentLoaded', () => {
    const nickname = document.getElementById('nickname');
    const static = document.getElementById('static');
    const discord = document.getElementById('discord');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm-password');
    const form = document.querySelector('#form');

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
        nickname: (event) => validateNicknameForm(event.target),
        static: (event) => validateStaticForm(event.target),
        discord: (event) => validateDiscordForm(event.target),
        password: (event) => validatePasswordForm(event.target),
        confirmPassword: (event) => validateConfirmForm(event.target)
    };

    function addValidationListener(field) {
        const listener = ModalValidationListeners[field.id];
        if (listener) {
            field.addEventListener('input', listener);
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

    enableFields([nickname, static, discord, password, confirmPassword]);

    function validateNicknameForm(input) {
        if (!input || input.value.trim() === '') {
            showError(input, 'Поле не может быть пустым');
            return false;
        }

        const pattern = /^[A-Z][a-z]+ [A-Z][a-z]+$/;
        const value = input.value.trim();

        if (!pattern.test(value)) {
            showError(input, 'Введите данные в формате "Nick Name"');
            return false;
        }

        clearError(input);
        return true;
    }

    function validateStaticForm(input) {
        if (!input || input.value.trim() === '') {
            showError(input, 'Поле не может быть пустым');
            return false;
        }

        const pattern = /^\d{1,7}$/;
        const value = input.value.trim();

        if (!pattern.test(value)) {
            showError(input, 'Введите данные в формате "static"');
            return false;
        }

        clearError(input);
        return true;
    }

    function validateDiscordForm(input) {
        if (!input || input.value.trim() === '') {
            showError(input, 'Поле не может быть пустым');
            return false;
        }

        const pattern = /^\d{17,21}$/;
        const value = input.value.trim();

        if (!pattern.test(value)) {
            showError(input, 'Введите данные в формате "discord ID"');
            return false;
        }

        clearError(input);
        return true;
    }

    function validatePasswordForm(input) {
        const value = input.value.trim();

        if (value.length < 10) {
            showError(input, 'Пароль должен содержать не менее 10 символов');
            return false;
        }

        const pattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{10,}$/;

        if (!pattern.test(value)) {
            showError(input, 'Пароль должен содержать заглавные и строчные буквы, цифры и специальные символы');
            return false;
        }

        clearError(input);
        return true;
    }

    function validateConfirmForm(input) {
        const confirmValue = input.value.trim();
        const passwordValue = document.getElementById('password').value.trim();

        if (confirmValue === '') {
            showError(input, 'Поле не может быть пустым');
            return false;
        }

        if (confirmValue !== passwordValue) {
            showError(input, 'Пароли не совпадают');
            return false;
        }

        clearError(input);
        return true;
    }

    form.addEventListener('submit', (event) => {
        let isValid = true;

        const inputs = [nickname, static, discord, password, confirmPassword];
        inputs.forEach(input => {
            const listener = ModalValidationListeners[input.id];
            if (listener && !listener({ target: input })) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
        }
    });
});
