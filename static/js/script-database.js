document.querySelectorAll('.rank-list')?.forEach(rankList => {
    new Sortable(rankList, {
        animation: 150,
        draggable: '.rank-item:not([data-leader="true"])', 

        onStart(evt) {
            const leaderItem = evt.from.querySelector('[data-leader="true"]');
            if (leaderItem) {
                leaderItem.setAttribute('draggable', 'false');
            }
        },

        onEnd(evt) {
            evt.from.querySelectorAll('.rank-item').forEach(item => {
                if (item.getAttribute('data-leader') !== 'true') {
                    item.setAttribute('draggable', 'true');
                }
            });

            updateRankIds(evt.from);
        }
    });
});

    function updateRankIds(list) {
    let index = list.querySelectorAll('.rank-item').length; 
    list.querySelectorAll('.rank-item').forEach(item => {
        const newId = index--; 
        const rankIdInput = item.querySelector('.rank-id');

        if (rankIdInput) {
            rankIdInput.value = newId;
        }

        if (item.getAttribute('data-recon') === 'true') {
            item.setAttribute('data-id', newId);

            if (rankIdInput) {
                rankIdInput.value = newId;
            }
        }
    });
}

    function filterRanksByFraction(fraction) {
        document.querySelectorAll('.fraction-group').forEach(group => {
            if (!fraction || group.dataset.fraction === fraction) {
                group.style.display = '';
            } else {
                group.style.display = 'none';
            }
        });
    }

    let ranksToAdd = [];

    function addRank(fraction) {
        const rankList = document.getElementById(`${fraction}-list`);
        const newId = generateNewId(rankList);

        const newItem = document.createElement('li');
        newItem.className = 'rank-item';
        newItem.setAttribute('data-id', newId);
        newItem.setAttribute('data-leader', 'false');
        newItem.setAttribute('data-recon', 'true');
        newItem.innerHTML = `
            <input type="text" class="rank-id" value="${newId}" readonly>
            <input type="text" class="rank-name" value="Новый ранг">
            <button class="delete-rank" onclick="deleteRank('${fraction}', ${newId})">Удалить</button>
        `;

        rankList.appendChild(newItem);


        console.log('Новый ранг добавлен:', ranksToAdd);

        updateRankIds(rankList);
    }

    function generateNewId(rankList) {
        let maxId = 0;
        rankList.querySelectorAll('.rank-item').forEach(item => {
            const id = parseInt(item.querySelector('.rank-id').value, 10);
            if (id > maxId) maxId = id;
        });
        return maxId + 1;
    }

    let ranksToDelete = [];

    function deleteRank(fraction, id) {
    const rankItem = document.querySelector(`[data-fraction="${fraction}"] [data-id="${id}"]`);
    if (rankItem) {
        if (rankItem.getAttribute('data-recon') === 'true') {

        } else {
            ranksToDelete.push({
                organ: fraction,
                id: id
            });
        }

        rankItem.remove();
        updateRankIds(document.getElementById(`${fraction}-list`));
    }
}

function saveRanks() {
    const updatedRanks = {};

    document.querySelectorAll('.fraction-group').forEach(group => {
        const fraction = group.dataset.fraction;
        const ranks = [];
        group.querySelectorAll('.rank-item').forEach(item => {
            const leaderSpan = item.querySelector('.leader-label');
            const isLeader = leaderSpan !== null;

            ranks.push({
                id: parseInt(item.querySelector('.rank-id').value),
                name: item.querySelector('.rank-name').value,
                leader: isLeader
            });
        });
        updatedRanks[fraction] = ranks;
    });

    const reconElements = document.querySelectorAll('[data-recon="true"]');
    reconElements.forEach(element => {
        rankidadd = element.querySelector('.rank-id').value;
        ranknameadd = element.querySelector('.rank-name').value;
        element.setAttribute('data-recon', 'false');

        const deleteButton = element.querySelector('.delete-rank'); 
        const onclickAttr = deleteButton.getAttribute('onclick'); 
        const fractionMatch = onclickAttr.match(/deleteRank\('([^']+)'/); 
        const fraction = fractionMatch ? fractionMatch[1] : null;

        ranksToAdd.push({
        organ: fraction,
        id: rankidadd,
        name: ranknameadd,
        leader: false
    });
    });

    const dataToSend = {
        updated_ranks: updatedRanks,
        ranks_to_delete: ranksToDelete,
        ranks_to_add: ranksToAdd
    };

    console.log('Saving ranks:', dataToSend);

    ranksToDelete = [];
    ranksToAdd = [];

    fetch('/save_ranks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    }).then(response => {
        if (response.ok) {
            alert('Изменения сохранены!');
        } else {
            alert('Ошибка при сохранении.');
        }
    });
}
    
    document.querySelectorAll('.rank-list').forEach(rankList => {
        new Sortable(rankList, {
            animation: 150,
            onEnd: function (evt) {
                console.log('Rank reordered:', evt);
            }
        });
    });

    document.querySelectorAll('.user-row').forEach(row => {
        row.addEventListener('dblclick', function() {
            const userId = this.getAttribute('data-user-id');
            
            window.location.href = `/database_getdata?user_id=${userId}`;
        });
    });
    

    function showTab(tabName) {
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });
        const selectedTab = document.getElementById(tabName);
        if (selectedTab) {
            selectedTab.style.display = 'block';
        }
    }
    function filterRanksByFraction(fraction) {
        document.querySelectorAll('.fraction-group').forEach(group => {
            if (!fraction || group.dataset.fraction === fraction) {
                group.style.display = '';
            } else {
                group.style.display = 'none';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        showTab('users');
        filterRanksByFraction('LSPD');
    });

    if (document.getElementById('toggleKaHistoryBtn')) {
        document.getElementById('toggleKaHistoryBtn').addEventListener('click', function() {
            var kaHistory = document.getElementById('kaHistory');
            var button = document.getElementById('toggleKaHistoryBtn');
            
            if (kaHistory.style.display === 'none') {
                kaHistory.style.display = 'flex';
                document.querySelectorAll('#overlay').forEach(o => {
                    o.classList.add('active');
                });
            
                setTimeout(() => {
                    kaHistory.classList.remove('hidden-modal');
                    kaHistory.classList.add('show-modal');
                }, 10);

                button.textContent = 'Скрыть Историю КА'; 
            } else {
                kaHistory.classList.remove('show-modal');
                kaHistory.classList.add('hidden-modal');

                setTimeout(() => {
                    kaHistory.style.display = 'none';
                    document.querySelectorAll('#overlay').forEach(o => {
                        o.classList.remove('active');
                    });
                }, 450);
                button.textContent = 'Показать Историю КА';
            }
        });
    }
    let debounceTimer;

    document.getElementById('searchInput')?.addEventListener('input', debounce(performSearch, 500));
    document.getElementById('filter')?.addEventListener('change', performSearch);

    function debounce(callback, delay) {
        return function (...args) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => callback(...args), delay);
        };
    }

    function performSearch() {
        const searchInput = document.getElementById('searchInput').value.trim();
        const filterValue = document.getElementById('filter').value;

        if (!searchInput && !filterValue) {
            updateTable([]);
            return;
        }

        setLoading(true);

        fetch(`/getSearchUser?inputVal=${encodeURIComponent(searchInput)}&filterVal=${encodeURIComponent(filterValue)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка при запросе на сервер');
                }
                return response.json();
            })
            .then(data => {
                setLoading(false);
                if (data.success) {
                    updateTable(data.results);
                } else {
                    updateTable([]);
                    console.error('Нет данных для отображения');
                }
            })
            .catch(error => {
                setLoading(false); 
                console.error('Ошибка при запросе:', error);
            });
    }

    function updateTable(users) {
        const tableBody = document.querySelector('table tbody');
        if (!tableBody) {
            console.error('Таблица не найдена в DOM.');
            return;
        }

        tableBody.innerHTML = '';

        if (users.length === 0) {
            tableBody.innerHTML = `
                <tr class="empty-message">
                    <td colspan="5">Данные не найдены</td>
                </tr>
            `;
            return;
        }

        users.forEach(user => {
            const row = document.createElement('tr');
            row.classList.add('user-row');
            row.dataset.userId = user.id;

            row.innerHTML = `
                <td>${user.nikname}</td>
                <td>${user.static}</td>
                <td>${user.organ}</td>
                <td>${user.curr_rank}</td>
                <td>${user.discordname}</td>
            `;

            tableBody.appendChild(row);
        });
    }

    function setLoading(isLoading) {
        if (isLoading) {
            document.body.classList.add('loading');
        } else {
            document.body.classList.remove('loading');
        }
    }

    function checkPermissions(tabName) {
        fetch('/check_permissions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showTab(tabName); 
            } else {
                showNotification(data.message, true); 
            }
        })
        .catch(error => console.error('Ошибка при проверке прав:', error));
    }
    
    document.addEventListener('DOMContentLoaded', function () {
        let formChanged = false;
        const formElements = document.querySelectorAll('#database-change input, #database-change select, #database-change textarea');

        formElements.forEach(element => {
            element.addEventListener('change', function() {
                formChanged = true;
            });
        });

        const customAlert = document.getElementById('customAlert');
        const confirmAlert = document.getElementById('confirmAlert');
        const cancelAlert = document.getElementById('cancelAlert');

        document.querySelector('.close-btn')?.addEventListener('click', function(event) {
            if (formChanged) {
                customAlert.style.display = 'flex';
                event.preventDefault(); 
            }
        });

        confirmAlert?.addEventListener('click', function() {
            customAlert.style.display = 'none';
            window.history.back();
        });

        cancelAlert?.addEventListener('click', function() {
            customAlert.style.display = 'none';
        });

        document.getElementById('database-change')?.addEventListener('submit', function(event) {
            event.preventDefault(); 
            formChanged = false;
    
            const formData = new FormData(event.target);
            const dataObject = Object.fromEntries(formData.entries());
    
            fetch('/database_change', {
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
        });
    });

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

    function getSelectedRoles() {
        const fraction = document.getElementById('fraction').value;
        const roles = [];

        const fractionGroup = document.querySelector(`.fraction-group[data-fraction="${fraction}"]`);

        if (!fractionGroup) {
            return { fraction, roles };
        }

        fractionGroup.querySelectorAll('.role-table tbody tr').forEach(row => {
            const roleId = row.querySelector('[data-id]')?.getAttribute('data-id');
            if (!roleId) return;

            const roleData = {
                id: roleId,
                dep_lider: row.querySelector('[data-role="dep_lider"]')?.checked || false,
                high_staff: row.querySelector('[data-role="high_staff"]')?.checked || false,
                judge: row.querySelector('[data-role="judge"]')?.checked || false,
                prosecutor: row.querySelector('[data-role="prosecutor"]')?.checked || false,
                lawyer: row.querySelector('[data-role="lawyer"]')?.checked || false,
                news_creation: row.querySelector('[data-role="news_creation"]')?.checked || false,
                documentation_creation: row.querySelector('[data-role="documentation_creation"]')?.checked || false,
            };

            roles.push(roleData);
        });
        return { fraction, roles };
    }

    document.getElementById('save-roles')?.addEventListener('click', function() {
        const data = getSelectedRoles();

        console.log(data);

        fetch('/save_roles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message)
            } else {
                showNotification(data.message, true)
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification('Произошла ошибка при сохранении ролей', true);
        });
    });
    
    