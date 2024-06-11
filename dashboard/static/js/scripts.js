window.price_avg = {};

function changeSVG(event) {
    var btn = event.currentTarget; // Получаем текущую кнопку
    var parentDiv = btn.closest('.checkbox'); // Получаем родительский div с классом 'checkbox'
    var img = btn.querySelector('img'); // Получаем изображение внутри кнопки
    var filterCheck = parentDiv.querySelector('.filterCheck');
    var nameText = parentDiv.querySelector('.nameText');


    if (img.src.includes('gala--settings.svg')) {
        img.src = 'static/img/Remove--Streamline-Ultimate.svg';
        filterCheck.style.display = 'flex';
        nameText.style.display = 'none';

    } else {
        img.src = 'static/img/gala--settings.svg';
        filterCheck.style.display = 'none';
        nameText.style.display = 'block';
    }
}

var buttons = document.querySelectorAll('.filter');
buttons.forEach(function (button) {
    button.addEventListener('click', changeSVG);
});


function decreaseFilterNumber(event) {
    var btn = event.currentTarget; // Получаем текущую кнопку
    var parentDiv = btn.closest('.checkbox'); // Получаем родительский div с классом 'checkbox'
    var filterInput = parentDiv.querySelector('.filterNumber'); // Получаем поле ввода внутри родительского div
    var currentValue = parseInt(filterInput.value);
    if (currentValue > 0) {
        filterInput.value = currentValue - 1;
    }
}

function increaseFilterNumber(event) {
    var btn = event.currentTarget; // Получаем текущую кнопку
    var parentDiv = btn.closest('.checkbox'); // Получаем родительский div с классом 'checkbox'
    var filterInput = parentDiv.querySelector('.filterNumber'); // Получаем поле ввода внутри родительского div
    var currentValue = parseInt(filterInput.value);
    filterInput.value = currentValue + 1;
}


var decreaseButtons = document.querySelectorAll('.btnPlusMinus img[src="/static/img/minus.svg"]');
decreaseButtons.forEach(function (img) {
    img.parentElement.addEventListener('click', decreaseFilterNumber);
});

var increaseButtons = document.querySelectorAll('.btnPlusMinus img[src="/static/img/plus.svg"]');
increaseButtons.forEach(function (img) {
    img.parentElement.addEventListener('click', increaseFilterNumber);
});


function resetFilters() {
    // Находим все поля ввода и обнуляем их значения
    var filterInputs = document.querySelectorAll('.filterNumber');
    filterInputs.forEach(function (input) {
        input.value = 0;
    });

    // Скрываем все элементы с классом 'filterCheck'
    var filterChecks = document.querySelectorAll('.filterCheck');
    filterChecks.forEach(function (filterCheck) {
        filterCheck.style.display = 'none';
    });

    // Показываем все элементы с классом 'nameText'
    var nameTexts = document.querySelectorAll('.nameText');
    nameTexts.forEach(function (nameText) {
        nameText.style.display = 'block';
    });

    // Сбрасываем изображения на исходные (если нужно)
    var filterButtons = document.querySelectorAll('.filter img');
    filterButtons.forEach(function (img) {
        img.src = 'static/img/gala--settings.svg';
    });

    Object.entries(window.price_avg).forEach(([key, value]) => {
        var div = document.getElementById("avg_" + key);
        div.textContent = value;
        var parrent = div.parentElement;
        var perc = parrent.querySelector(".procent");
        perc.textContent = "0%";


    });
}

// Назначаем обработчик события для кнопки "Отменить фильтры"
var resetButton = document.querySelector('.btn:nth-child(1)'); // предположительно, это первая кнопка
if (resetButton) {
    resetButton.addEventListener('click', resetFilters);
}


function applyFilters() {
    // Обрабатываем каждую строку с классом 'checkbox'
    var checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach(function (checkbox) {
        var filterCheck = checkbox.querySelector('.filterCheck');
        var nameText = checkbox.querySelector('.nameText');
        var filterNumber = checkbox.querySelector('.filterNumber');
        var itemTextes = checkbox.querySelectorAll('.itemText');
        var percentages = checkbox.querySelectorAll('.procent');

        if (filterCheck && filterCheck.style.display === 'flex' && filterNumber) {
            // Получаем процент из фильтра
            var percentage = parseFloat(filterNumber.value);

            // Преобразуем значение в ячейке itemText в число и умножаем на (1 + процент/100)
            let i = 0;
            itemTextes.forEach(function (itemText) {
                var currentPrice = parseFloat(itemText.innerText);
                var newPrice = currentPrice * (1 + percentage / 100);
                
                // Обновляем значение в ячейке itemText
                var newPriceString = price[1] + " - " + newPrice.toFixed(2);
                itemText.textContent = newPrice.toFixed(2);; // округляем до двух знаков после запятой
                percentages[i].textContent = percentage + "%";
                i = i + 1;
                
            });
            // Сбрасываем значение фильтра
            filterNumber.value = 0;
            console.log(window.price_avg);
            // Сворачиваем фильтр и отображаем название колонки
            filterCheck.style.display = 'none';
            nameText.style.display = 'block';
        }
    });

    // Сбрасываем изображения на исходные
    var filterButtons = document.querySelectorAll('.filter img');
    filterButtons.forEach(function (img) {
        img.src = 'static/img/gala--settings.svg'; // путь к исходному изображению
    });
}

// Назначаем обработчик события для кнопки "Применить фильтры"
var applyButton = document.querySelector('#apply_filter'); // предположительно, это третья кнопка в .buttons
if (applyButton) {
    applyButton.addEventListener('click', applyFilters);
}

document.getElementById('export-button').addEventListener('click', function () {
    if (confirm('Подтвердить действие')) {
        fetch('/export_to_excel/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                } else {
                    throw new Error('Network response was not ok.');
                }
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'details.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }
});

document.getElementById('add-page-button').addEventListener('click', function () {
    if (confirm('Подтвердить действие')) {
        const articles = document.querySelectorAll('.itemText[name="article-data"]');
        const maybePrice = document.querySelectorAll('.itemText[name="maybe-price"]');
        const newPrice = document.querySelectorAll('.itemText[name="new-price"]');

        let addData = [];
        const data = [];

        if (articles.length === maybePrice.length && articles.length === newPrice.length) {
            for (let i = 0; i < articles.length; i++) {
                const articleText = articles[i].textContent.trim();
                const maybePriceText = maybePrice[i].textContent.trim();
                const newPriceText = newPrice[i].value.trim();
                if (newPriceText == "") {
                    addData = [articleText, maybePriceText];
                } else {
                    addData = [articleText, newPriceText];
                }
                data.push(addData);
            }

            // Преобразование данных в JSON строку
            const jsonData = JSON.stringify(data);
            console.log(jsonData);
            fetch('/upload_completed_products/', {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                method: 'POST',
                body: JSON.stringify(data),
            })
                .then(response => response.json())
                .then(responseData => {
                    console.log(responseData);
                    alert(responseData.message || responseData.error);
                })
                .catch(error => {
                    console.error(error);
                    alert('Error uploading file');
                });

            console.log(data);
        } else {
            console.error('Длины массивов не совпадают');
        }
    }
});

const fileInput = document.getElementById('file-input');
const fileUploadButton = document.getElementById('file-upload-button');

fileUploadButton.addEventListener('click', function () {
    fileInput.click(); // При клике на кнопку вызываем клик на скрытом input
});

fileInput.addEventListener('change', function () {
    const file = fileInput.files[0];
    if (file) {
        const validMimeTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];

        if (!validMimeTypes.includes(file.type)) {
            alert('Пожалуйста, загрузите файл формата Excel.');
            fileUploadButton.textContent = 'Добавить файл';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Отправляем файл на сервер
        fetch('/upload/', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                console.log('Успех:', data);
                fileUploadButton.textContent = 'Файл загружен';
            })
            .catch((error) => {
                console.error('Ошибка:', error);
                fileUploadButton.textContent = 'Ошибка загрузки';
            });
    } else {
        fileUploadButton.textContent = 'Добавить файл';
    }
});

