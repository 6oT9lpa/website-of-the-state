document.documentElement.style.setProperty('--screen-width', `${window.innerWidth}px`);
document.documentElement.style.setProperty('--screen-height', `${window.innerHeight}px`);

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get('uid');
    document.querySelectorAll('#uidcompliant').forEach(inp => {
        inp.value = uid;
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
        });
    }

    function setupModalToggle(openBtn, closeBtn, modal) {
        if (openBtn && closeBtn && modal) {
            openBtn.addEventListener('click', () => showModal(modal));
            closeBtn.addEventListener('click', () => hideModal(modal));
        }
    }

    const modals = [
        { openBtn: '#open-btn-1', closeBtn: '#close-btn-1', modal: '#modal-1' },
        { openBtn: '#open-btn-2', closeBtn: '#close-btn-2', modal: '#modal-2' },
        { openBtn: '#open-btn-3', closeBtn: '#close-btn-3', modal: '#modal-3' },
        { openBtn: '#open-btn-4', closeBtn: '#close-btn-4', modal: '#modal-4' },
        { openBtn: '#open-btn-5', closeBtn: '#close-btn-5', modal: '#modal-5' },
        { openBtn: '#open-btn-6', closeBtn: '#close-btn-6', modal: '#modal-6' },
        { openBtn: '#open-btn-7', closeBtn: '#close-btn-7', modal: '#modal-7' },
        { openBtn: '#open-btn-8', closeBtn: '#close-btn-8', modal: '#modal-8' },
    ];

    modals.forEach(({ openBtn, closeBtn, modal }) => {
        setupModalToggle(document.querySelector(openBtn), document.querySelector(closeBtn), document.querySelector(modal));
    });

    setupDropdown(document.querySelector('#dropdown-1'), document.querySelector('#dropdown-btn-1'), document.querySelector('#dropdown-menu-1'), 'action-1');
    setupDropdown(document.querySelector('#dropdown-2'), document.querySelector('#dropdown-btn-2'), document.querySelector('#dropdown-menu-2'), 'action-2');
    setupDropdown(document.querySelector('#dropdown-3'), document.querySelector('#dropdown-btn-3'), document.querySelector('#dropdown-menu-3'), 'action-3');
    setupDropdown(document.querySelector('#dropdown-4'), document.querySelector('#dropdown-btn-4'), document.querySelector('#dropdown-menu-4'), 'action-4');
    setupDropdown(document.querySelector('#dropdown-5'), document.querySelector('#dropdown-btn-5'), document.querySelector('#dropdown-menu-5'), 'action-5');
    setupDropdown(document.querySelector('#dropdown-6'), document.querySelector('#dropdown-btn-6'), document.querySelector('#dropdown-menu-6'), 'action-6');

    function initInputGroup(addButtonSelector, groupSelector, deleteButtonSelector) {
        let counter = 1;
        const maxInputs = 11;
    
        const addDefendaButton = document.querySelector(addButtonSelector); 
        const groupDefendaDiv = document.querySelector(groupSelector); 
        const groupBtnDecision = document.querySelector(deleteButtonSelector);
        
        const deleteButton = document.createElement("a");
        deleteButton.classList.add("btn-add-decision");
        deleteButton.textContent = "Удалить";
        deleteButton.style.display = "none"; 
        
        deleteButton.addEventListener("click", function (e) {
            e.preventDefault();
            const inputWrappers = Array.from(groupDefendaDiv.children);
    
            const lastInputWrapper = groupDefendaDiv.lastElementChild;
            if (lastInputWrapper) {
                lastInputWrapper.remove();
                counter--;
                updateInputNumbers();
    
                if (counter == 2) {
                    deleteButton.style.display = "none";
                }
            }
        });
        
        groupBtnDecision.appendChild(deleteButton);
    
        addDefendaButton.addEventListener("click", function(e) {
            e.preventDefault();

            if (counter >= maxInputs) {
                return;  
            }
    
            const newContentDiv = document.createElement("div");
            newContentDiv.classList.add("form-input-modal");
            newContentDiv.id = `decision-input-${counter}`;
    
            const inputWrapper = document.createElement("div");
            inputWrapper.style.display = "flex";
            inputWrapper.style.alignItems = "center";
    
            const inputNumber = document.createElement("span");
            inputNumber.textContent = `${counter}.`;
            inputNumber.style.fontWeight = "bold";
            inputNumber.style.fontSize = "13px";
    
            const newInput = document.createElement("input");
            newInput.type = "text";
            newInput.id = `decision_${counter}`;
            newInput.name = "decision";
            newInput.placeholder = "Введите пункт определения";
            
            newContentDiv.appendChild(newInput);
            inputWrapper.appendChild(inputNumber);
            inputWrapper.appendChild(newContentDiv);
            groupDefendaDiv.appendChild(inputWrapper);
    
            counter++;
            if (counter > 1) {
                deleteButton.style.display = "inline-block";
            }
        });
    
        function updateInputNumbers() {
            const inputWrappers = Array.from(groupDefendaDiv.children);
            let number = 1;
            inputWrappers.forEach((wrapper) => {
                const inputNumber = wrapper.querySelector("span");
                if (inputNumber) {
                    inputNumber.textContent = `${number}.`;
                    number++;
                }
            });
        }
    }   
    
    if (document.getElementById('modal-1')) {
        initInputGroup("#btn-0", "#group-0", "#group-btn-0");
    }

    if (document.getElementById('modal-2')) {
        initInputGroup("#btn-1", "#group-1", "#group-btn-1");
    }

    if (document.getElementById('modal-6')) {
        initInputGroup("#btn-2", "#group-2", "#group-btn-2");
    }

    if (document.getElementById('modal-7')) {
        initInputGroup("#btn-3", "#group-3", "#group-btn-3");
    }

    document.querySelectorAll('.submit-btn input').forEach(button => {
        button.addEventListener('click', (event) => {
            event.stopPropagation(); 
        });
    });

    let isHovered = false;
    let isAnimating = false;
    let hoverTimeout;

    const sidebar = document.querySelector('.sidebar-container');
    const maincontent = document.querySelector('.main-content-complaint');
    const form = document.getElementById('addLink');

    function isFormElement(target) {
        const form = document.getElementById('addLink');
        return form && form.contains(target);  
    }

    function isOpenButton(target) {
        return modals.some(modal => document.querySelector(modal.openBtn) === target);
    }

    sidebar.addEventListener('mouseenter', (event) => {
        if (isHovered || isAnimating || isFormElement(event.target) || isOpenButton(event.target)) return;
        isHovered = true;
        isAnimating = true;

        clearTimeout(hoverTimeout);
        sidebar.classList.remove('hover-out');
        hoverTimeout = setTimeout(() => {
            sidebar.classList.add('hover-in');
            hoverTimeout = setTimeout(() => {
                isAnimating = false;
            }, 1000);
            hoverTimeout = setTimeout(() => {
                maincontent.style.width = 'calc(var(--screen-width) - 300px)';
            }, 200);
        }, 100);
    });

    sidebar.addEventListener('mouseleave', (event) => {
        if (!isHovered || isAnimating || isFormElement(event.target) || isOpenButton(event.target)) return; 
        isHovered = false;
        isAnimating = true;

        clearTimeout(hoverTimeout);
        sidebar.classList.remove('hover-in');
        hoverTimeout = setTimeout(() => {
            sidebar.classList.add('hover-out');
            hoverTimeout = setTimeout(() => {
                isAnimating = false;
            }, 1000);
            hoverTimeout = setTimeout(() => {
                maincontent.style.width = 'calc(var(--screen-width) - 400px)';
            }, 80);
        }, 100);
    });

    sidebar.addEventListener('click', (event) => {
        if (isFormElement(event.target) || isOpenButton(event.target)) return;
        sidebar.classList.toggle('open');
        maincontent.style.width = 'calc(var(--screen-width) - 400px)';
        maincontent.classList.toggle('open');
    });
});

document.querySelector('#claim-processing')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const decisions = formData.getAll('decision'); 
    const payload = {
        ...Object.fromEntries(formData.entries()), 
        decision: decisions
    };

    const validProcessing = ['accept', 'reject', 'hold'];
    if (!validProcessing.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите обстоятельства', true);
        return;
    }

    if (!data.consideration || !data.consideration.trim()) {   
        showNotification('Введите рассмотрение, ссылаясь на закон', true);
        return;
    }

    fetch('/create_court_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);

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
})

document.querySelector('#court-hearing')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const decisions = formData.getAll('decision'); 
    const payload = {
        ...Object.fromEntries(formData.entries()), 
        decision: decisions
    };

    const validProcessing = ['reassign', 'appoint'];
    if (!validProcessing.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите обстоятельства', true);
        return;
    }

    if (!data.consideration || !data.consideration.trim()) {   
        showNotification('Введите рассмотрение, ссылаясь на закон', true);
        return;
    }

    if (!data.time || !data.time.trim()) {
        showNotification('Введите время судебного заседания', true);
        return;
    }
    
    fetch('/create_court_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
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
})

document.querySelector('#decision-court')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const decisions = formData.getAll('decision'); 
    const payload = {
        ...Object.fromEntries(formData.entries()), 
        decision: decisions
    };

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите обстоятельства', true);
        return;
    }

    if (!data.consideration || !data.consideration.trim()) {   
        showNotification('Введите рассмотрение, ссылаясь на закон', true);
        return;
    }

    fetch('/create_court_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
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
})

document.querySelector('#prosecutor_delo')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const validDelo = ['accusatory', 'blameless'];
    if (!validDelo.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    fetch('/create_prosecutor', {
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
})

document.querySelector('#start_invest')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    fetch('/create_prosecutor', {
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
})

document.querySelector('#create-petition')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const validType = ['freeform', 'svidetel', 'expert', 'otvod'];
    if (!validType.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    const validNickname = ['svidetel', 'expert', 'otvod'];
    if (validNickname.includes(data.action)) {
        if (!data.nickname || !data.nickname.trim()) {
            showNotification('Введите nickname, случае выбора действия "Свидетель", "Эксперт" или "Отвод"', true);
            return;
        }
        if (!data.static || !data.static.trim()) {
            showNotification('Введите static, случае выбора действия "Свидетель", "Эксперт" или "Отвод"', true);
            return;
        }
    }

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите тело ходатайства!', true);
        return;
    }

    fetch('/create_petition', {
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
})

document.querySelector('#create-court-petition')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    const decisions = formData.getAll('decision'); 
    const payload = {
        ...Object.fromEntries(formData.entries()), 
        decision: decisions
    };

    const validType = ['true-petition', 'false-petition'];
    if (!validType.includes(data.action)) {
        showNotification('Выберите действие', true);
        return;
    }

    if (!data.findings || !data.findings.trim()) {
        showNotification('Введите обстоятельства', true);   
        return;
    }

    if (!data.consideration || !data.consideration.trim()) {   
        showNotification('Введите рассмотрение, ссылаясь на закон', true);
        return;
    }

    fetch('/create_court_pettion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            
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
})

if (status == 'Created') {
    document.addEventListener('DOMContentLoaded', function () {
        const form = document.getElementById('addLink');
        const submitContainer = document.getElementById('btn-container-1');

        function getInputs() {
            return form.querySelectorAll('input[type="url"], input[type="text"]');
        }

        function checkInputs() {
            const hasValue = Array.from(getInputs()).some(input => input.value.trim() !== '');
            submitContainer.style.display = hasValue ? 'block' : 'none';
        }

        getInputs().forEach(input => {
            input.addEventListener('input', checkInputs);
        });

        checkInputs();
    });
}

document.querySelector('#addLink')?.addEventListener('submit', (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const evidences = formData.getAll('evidence'); 

    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)\/(watch\?v=[\w-]+|.+)$/;
    const rutubeRegex = /^(https?:\/\/)?(www\.)?rutube\.ru\/video\/[a-zA-Z0-9]+\/?$/;
    const yapixRegex = /^(https?:\/\/)?(www\.)?yapix\.ru\/video\/[a-zA-Z0-9]+\/?$/;
    const imgurRegex = /^(https?:\/\/)?(www\.)?imgur\.com\/[a-zA-Z0-9]+\/?$/;

    paymentProofUrl = data.paymentProof;
    const invalidPaymentProof = paymentProofUrl && !(yapixRegex.test(paymentProofUrl) || imgurRegex.test(paymentProofUrl));

    const invalidEvidence = evidences.find(url => 
        !youtubeRegex.test(url) && 
        !rutubeRegex.test(url) && 
        !yapixRegex.test(url) && 
        !imgurRegex.test(url)
    );

    if (invalidEvidence) {
        showNotification('Введите корректную ссылку youtube/rutube/yapix/imgur в поле доказательств', true);
        return;
    } else if (invalidPaymentProof) {
        showNotification('Введите корректную ссылку yapix/imgur в поле оплаты гос. пошлины', true);
        return;
    }
    const payload = {
        ...data,
        evidence: evidences
    };

    fetch('/add_link_court', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })

    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            
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
})