document.documentElement.style.setProperty('--screen-width', `${window.innerWidth}px`);
document.documentElement.style.setProperty('--screen-height', `${window.innerHeight}px`);
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar-container');
    const maincontent = document.querySelector('.main-content-complaint');
    const dropdownBtn = document.querySelector('.dropdown-btn');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    const dropdown = document.querySelector('.dropdown');
    const modalcomplaint = document.querySelector('.modal-processing-complaint');
    const acceptjudge = document.querySelector('.accept-judge');
    const closeModalBtn = document.querySelector('#btn-modal-close');

    function showModal() {
        modalcomplaint.style.display = 'flex';
        document.querySelectorAll('#overlay').forEach(o => {
            o.classList.add('active');
        });
        
        setTimeout(() => {
            modalcomplaint.classList.remove('hidden-modal-district')
            modalcomplaint.classList.add('show-modal-district')
        }, 10)
    }

    function hideModal() {
        modalcomplaint.classList.remove('show-modal-district')
        modalcomplaint.classList.add('hidden-modal-district')

        setTimeout(() => {
            modalcomplaint.style.display = 'none';
            document.querySelectorAll('#overlay').forEach(o => {
                o.classList.remove('active');
            });
        }, 450);
    }

    if (acceptjudge) {
        acceptjudge.addEventListener('click', showModal);
        closeModalBtn.addEventListener('click', hideModal);

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
            document.getElementById('action').value = action;
            dropdown.classList.remove('open');
            dropdownBtn.classList.remove('active');
        });

        let counter = 1; 

        const addDefendaButton = document.querySelector(".btn-add-input"); 
        const groupDefendaDiv = document.querySelector('.group-decision'); 
        const groupBtnDecision = document.querySelector('.group-btn-decision');
        
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

                if (counter <= 2) {
                    deleteButton.style.display = "none";
                }
            }
            
        });
        
        
        groupBtnDecision.appendChild(deleteButton);
        
        addDefendaButton.addEventListener("click", function(e) {
            e.preventDefault();
        
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


    let isHovered = false;
    let isAnimating = false;
    let hoverTimeout;

    sidebar.addEventListener('mouseenter', () => {
        if (isHovered || isAnimating) return;
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
                maincontent.style.width = 'calc(var(--screen-width) - 300px)'
            }, 200);
        }, 100);
    });

    sidebar.addEventListener('mouseleave', () => {
        if (!isHovered || isAnimating) return; 
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
                maincontent.style.width = 'calc(var(--screen-width) - 400px)'
            }, 80);
        }, 100);
    });

    sidebar.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        maincontent.style.width = 'calc(var(--screen-width) - 400px)';
        maincontent.classList.toggle('open');
    });
});
