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