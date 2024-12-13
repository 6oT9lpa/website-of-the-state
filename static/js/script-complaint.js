document.documentElement.style.setProperty('--screen-width', `${window.innerWidth}px`);
document.documentElement.style.setProperty('--screen-height', `${window.innerHeight}px`);
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const uid = urlParams.get('uid');
    document.querySelectorAll('#uidcompliant').forEach(inp => {
        inp.value = uid;
    });

    const sidebar = document.querySelector('.sidebar-container');
    const maincontent = document.querySelector('.main-content-complaint');
    const dropdownBtn = document.querySelector('.dropdown-btn');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    const dropdown = document.querySelector('.dropdown');

    const acceptjudge = document.querySelector('.accept-judge');
    const closeModalBtnjudge = document.querySelector('#btn-modal-close-judge');
    const acceptpettion = document.querySelector('.accept-petition');
    const closeModalBtnpettion = document.querySelector('#btn-modal-close-pettion');

    const modal1 = document.getElementById('modal-1');
    const modal2 = document.getElementById('modal-2');
    const modal3 = document.getElementById('modal-3');

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

    if (acceptpettion) {  
        const dropdownBtnpettion = document.querySelectorAll('.dropdown-btn-pettion');
        const dropdownMenupettion = document.querySelectorAll('.dropdown-menu-pettion');
        const dropdownpettion = document.querySelectorAll('.dropdown-pettion');
        
        const dropdownBtnpettionList = document.querySelector('.dropdown-btn-pettion-list');
        const dropdownMenupettionList = document.querySelector('.dropdown-menu-pettion-list');
        const dropdownpettionList = document.querySelector('.dropdown-pettion-list');

        
        if (modal3) {
            acceptpettion.addEventListener('click', () => showModal(modal3));
            closeModalBtnpettion.addEventListener('click',  () => hideModal(modal3));
        }

        if (modal2) {
            acceptpettion.addEventListener('click', () => showModal(modal2));
            closeModalBtnpettion.addEventListener('click',  () => hideModal(modal2));
        }

        dropdownBtnpettion.forEach(btn => {
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    dropdownpettion.forEach(main => {
                        if (main) { main.classList.toggle('open'); }
                    })
                    btn.classList.toggle('active');
                });
            }
        });
        
        document.addEventListener('click', (e) => {
            dropdownpettion.forEach(main => {
                if (main && !main.contains(e.target)) { main.classList.remove('open'); }
            })

            dropdownBtnpettion.forEach(btn => {
                if (btn && btn.contains(e.target)) { btn.classList.remove('active');}
            })
        });

        dropdownMenupettion.forEach(menu => {
            if (menu) {
                menu.addEventListener('click', (e) => {
                    e.preventDefault();
                    const action = e.target.dataset.action;

                    dropdownBtnpettion.forEach(btn => {
                        if (btn) { btn.textContent = e.target.textContent; btn.classList.remove('active');}
                    })

                    document.getElementById('action-pettion').value = action;
                    dropdownpettion.forEach(main => {
                        if (main) { main.classList.remove('open'); }
                    })
                    
                });
            }
        });

        if (modal2) {
            dropdownBtnpettionList.addEventListener('click', (e) => {
                e.preventDefault();
                dropdownpettionList.classList.toggle('open');
                dropdownBtnpettionList.classList.toggle('active');
            });
            
            document.addEventListener('click', (e) => {
                if (!dropdownpettionList.contains(e.target) && !dropdownBtnpettionList.contains(e.target)) {
                    dropdownpettionList.classList.remove('open');
                    dropdownBtnpettionList.classList.remove('active');
                }
            });
            
            dropdownMenupettionList.addEventListener('click', (e) => {
                e.preventDefault();
                const action = e.target.dataset.action;
                dropdownBtnpettionList.textContent = e.target.textContent;
                document.getElementById('action-pettion-list').value = action;
                dropdownpettionList.classList.remove('open');
                dropdownBtnpettionList.classList.remove('active');
            });

            let counter = 1; 

            const addDefendaButton = document.querySelector(".btn-add-input-pettion"); 
            const groupDefendaDiv = document.querySelector('.group-decision-pettion'); 
            const groupBtnDecision = document.querySelector('.group-btn-decision-pettion');
            
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
    }

    if (acceptjudge) {
        if (modal1) {
            acceptjudge.addEventListener('click', () => showModal(modal1));
            closeModalBtnjudge.addEventListener('click',  () => hideModal(modal1));
        }
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
