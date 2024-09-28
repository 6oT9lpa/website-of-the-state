const form = document.querySelector('form');
const discordIdInput = document.querySelector('.discord-id');
const discordNameInput = document.querySelector('.discord-name');
const staticInput = document.getElementById('static');
const nikNameInput = document.getElementById('nik-name');
const rankInput = document.getElementById('rank');
const formButton = document.querySelector('.form-button');
const errorDiv = document.createElement('div'); // Создаем div для вывода ошибок
errorDiv.classList.add('error-message'); // Добавляем класс для стилизации

form.insertBefore(errorDiv, formButton); // Вставляем div перед кнопкой отправки

formButton.addEventListener('click', (event) => {
  event.preventDefault();
  errorDiv.textContent = ''; // Очищаем предыдущие сообщения об ошибках

  let isValid = true;

  // Проверка Discord ID
  if (!/^\d{18}$/.test(discordIdInput.value)) {
    errorDiv.textContent = 'Некорректный Discord ID. Введите 18 цифр.';
    isValid = false;
  }

  // Проверка Discord Name
  if (!/^[a-zA-Z]{1,15}$/.test(discordNameInput.value)) {
    errorDiv.textContent = 'Некорректный Discord Name. Введите не более 15 букв.';
    isValid = false;
  }

  // Проверка Static
  if (!/^\d{1,5}$/.test(staticInput.value)) {
    errorDiv.textContent = 'Некорректный Static. Введите не более 5 цифр.';
    isValid = false;
  }

  // Проверка Nik Name
  if (!/^[a-zA-Z]+\s[a-zA-Z]+$/.test(nikNameInput.value) || nikNameInput.value.length > 45) {
    errorDiv.textContent = 'Некорректный Nik Name. Введите не более 45 букв, обязательно с пробелом между словами.';
    isValid = false;
  }

  // Проверка Rank
  if (!/^\d+$/.test(rankInput.value)) {
    errorDiv.textContent = 'Некорректный Rank. Введите целое число.';
    isValid = false;
  }

  if (isValid) {
    // Если все проверки пройдены, отправляем форму
    form.submit();
  }
});
