
    
const fractionSelect = document.getElementById('organ_change');
const rankSelect = document.getElementById('rank-select');

function updateRanks() {
    const selectedFraction = fractionSelect.value;
    rankSelect.innerHTML = '';

    if (ranks[selectedFraction]) {
        ranks[selectedFraction]
            .sort((a, b) => a.id - b.id)
            .forEach(rank => {
                const option = document.createElement('option');
                option.value = rank.id;
                option.textContent = `${rank.id} | ${rank.name}`;
                rankSelect.appendChild(option);
            });
    } else {
        const option = document.createElement('option');
        option.textContent = 'No ranks available';
        option.disabled = true;
        rankSelect.appendChild(option);
    }
}

fractionSelect?.addEventListener('change', updateRanks);
document.addEventListener('DOMContentLoaded', function() {
    if (fractionSelect) {
        updateRanks();
    }
});

let typingTimer;
const doneTypingInterval = 300;

document.getElementById('static').addEventListener('input', function(event) {
    clearTimeout(typingTimer);

    const staticValue = event.target.value;

    if (/[^0-9]/.test(staticValue)) {
        event.target.value = '';
        removeFireButton();
        document.getElementById('discord').value = '';
        document.getElementById('nickname').value = '';
        return;
    }

    if (staticValue.trim() === '') {
        removeFireButton();
        document.getElementById('discord').value = '';
        document.getElementById('nickname').value = '';
        return;
    }

    typingTimer = setTimeout(function() {
        fetch(`/getPlayerData?static=${staticValue}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (document.getElementById('discord').value !== data.discord) {
                        document.getElementById('discord').value = data.discord;
                    }
                    if (document.getElementById('nickname').value !== data.nickname) {
                        document.getElementById('nickname').value = data.nickname;
                    }
                    if (data.action !== 'Dismissal') {
                        addFireButton();
                    }
                } else {
                    removeFireButton();
                    document.getElementById('discord').value = '';
                    document.getElementById('nickname').value = '';
                }
            })
            .catch(error => {
                console.error('Ошибка при запросе:', error);
                removeFireButton();
                document.getElementById('discord').value = '';
                document.getElementById('nickname').value = '';
            });
    }, doneTypingInterval);
});

function addFireButton() {
    const existingButton = document.querySelector('.form-button-container .submit-btn-contanier .fire-btn');
    if (existingButton) return;

    const container = document.querySelector('.form-button-container');
    const fireButtonWrapper = document.createElement('div');
    fireButtonWrapper.classList.add('submit-btn-contanier');

    const fireButtonDiv = document.createElement('div');
    fireButtonDiv.classList.add('submit-btn');

    const fireButton = document.createElement('input');
    fireButton.type = 'submit';
    fireButton.value = 'Уволить';
    fireButton.classList.add('fire-btn');
    fireButtonDiv.appendChild(fireButton);
    fireButtonWrapper.appendChild(fireButtonDiv);
    container.appendChild(fireButtonWrapper);

    fireButton.addEventListener('click', function(event) {
        event.preventDefault();
        fireButton.classList.toggle('red');
        fireButtonDiv.classList.toggle('red');

        const dismissalField = document.getElementById('dismissal');
        if (dismissalField.value === 'dismissal') {
            dismissalField.value = 'none';
        } else {
            dismissalField.value = 'dismissal';
        }
    });
}

function removeFireButton() {
    const fireButtonWrapper = document.querySelector('.form-button-container .submit-btn-contanier .fire-btn');
    if (fireButtonWrapper) {
        fireButtonWrapper.closest('.submit-btn-contanier').remove();
    }
}

document.getElementById('form-audit').addEventListener('submit', function(event) {
    event.preventDefault(); 

    const formData = new FormData(event.target);
    const dataObject = Object.fromEntries(formData.entries());

    const fractionSelector = document.getElementById('organ_change');
    if (fractionSelector) {
        const fractionValue = dataObject.fraction;
        console.log(dataObject.fraction)
        const validFractions = ['LSPD', 'LSCSD', 'EMS', 'SANG', 'GOV', 'FIB', 'WN'];
        if (!validFractions.includes(fractionValue)) {
            showNotification("Нии...даа.... так делать!", true);
            return;
        }
    }
    /* 
    const nickname = dataObject.nickname;
    const nicknameRegex = /^[A-Za-z]+(?:\s[A-Za-z]+)*$/;
    if (!nicknameRegex.test(nickname)) {
        showNotification("Ник должен быть в формате 'Nick Name'", true);
        return;
    }
        */

    const discordId = String(dataObject.discord);
    const discordIdRegex = /^\d{17,19}$/;
    if (!discordIdRegex.test(discordId)) {
        showNotification("Discord ID должен быть числовым значением длиной от 17 до 19 символов.", true);
        return;
    }

    fetch('/audit', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
    },
        body: JSON.stringify(Object.fromEntries(formData.entries()))
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            document.getElementById('form-audit').reset()
            document.getElementById('discord').disabled = false;
            document.getElementById('nickname').disabled = false;
            const fireButtonWrapper = document.querySelector('.form-button-container .submit-btn-contanier .fire-btn');
            if (fireButtonWrapper) {
                fireButtonWrapper.closest('.submit-btn-contanier').remove(); 
            }

            setTimeout(() => {
                location.reload();
            }, 3000);

        } else {
            showNotification(data.message, true);
        }
    })
    .catch(error => {
        console.error('Произошла ошибка:', error);
        showNotification('Произошла ошибка при отправке данных', true);
    });
});