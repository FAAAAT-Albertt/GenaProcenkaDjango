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
        try {
            var div = document.getElementById("avg_" + key);
            div.textContent = value;
            var parrent = div.parentElement;
            var perc = parrent.querySelector(".procent");
            perc.textContent = "0%";
        } catch (err) {
            console.log("after");
        }


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
                var round_avg = (round_avg = newPrice % 10) <= 5 ? (parseInt(newPrice / 10) + 5 / 10) * 10 : (Math.round(parseInt(newPrice / 10) + round_avg / 10)) * 10;


                // Обновляем значение в ячейке itemText
                itemText.textContent = round_avg.toFixed(2);; // округляем до двух знаков после запятой
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

const div_detail = document.getElementById('detail')
const div_article = document.getElementById('article')
const div_price = document.getElementById('price')
const div_carreta = document.getElementById('carreta')
const div_amry = document.getElementById('amry')
const div_armtek = document.getElementById('armtek')
const div_emex = document.getElementById('emex')
const div_avg_price = document.getElementById('avg_price')
const div_change_price = document.getElementById('change_price')



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
                connect(true);
            })
            .catch((error) => {
                console.error('Ошибка:', error);
                fileUploadButton.textContent = 'Ошибка загрузки';
            });
    } else {
        fileUploadButton.textContent = 'Добавить файл';
    }
});


var prevButton = document.querySelector('.btnPrev');
if (prevButton) {
    prevButton.addEventListener('click', prevPage);
}

var nextButton = document.querySelector('.btnNext');
if (nextButton) {
    nextButton.addEventListener('click', nextPage);
}

function prevPage() {
    var checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach(function (checkbox) {
        var itemTextes = checkbox.querySelectorAll('.item');
        itemTextes.forEach(function (item) {
            checkbox.removeChild(item);
        })
    });

    window.socket.send(JSON.stringify({ 'message': "prev_page" }));
}

function nextPage() {
    var checkboxes = document.querySelectorAll('.checkbox');
    checkboxes.forEach(function (checkbox) {
        var itemTextes = checkbox.querySelectorAll('.item');
        itemTextes.forEach(function (item) {
            checkbox.removeChild(item);
        })
    });

    window.socket.send(JSON.stringify({ 'message': "next_page" }));
}

function connect(first) {
    if (first) {
        window.socket = new WebSocket("wss://mazda-ford.ru/ws_detail?from=site");
    } else {
        window.socket = new WebSocket("wss://mazda-ford.ru/ws_detail");
    }

    window.socket.onopen = function (e) {
        console.log("[open] Соединение установлено");
    };

    window.socket.onmessage = function (event) {
        var message = JSON.parse(event.data);

        var detail_div_new = `<div class="item minName"><p class="itemText">${message.detail}</p></div>`
        var article_div_new = `<div class="item minName"><p class="itemText" name="article-data">${message.article}</p></div>`
        var price_div_new = `<div class="item minName"><p class="itemText">${message.price}</p></div>`
        var carreta_div_new = `<div class="item" id="carreta_${message.article}"><p class="itemText">${message.carreta}</p></div>`
        var amry_div_new = `<div class="item" id="amry_${message.article}"><p class="itemText">${message.amry}</p></div>`
        var armtek_div_new = `<div class="item" id="armtek_${message.article}"><p class="itemText">${message.armtek}</p></div>`
        var emex_div_new = `<div class="item" id="emex_${message.article}"><p class="itemText">${message.emex}</p></div>`
        var avg_div_new = `<div class="item itemFlex"><p class="itemText" name="maybe-price" id="avg_${message.article}">-</p><p class="procent" id="#">0%</p></div>`
        var change_div_new = `<div class="item minName"><input class="itemText" name="new-price" type="text" placeholder="Введите сумму"></div>`
        div_detail.insertAdjacentHTML('beforeend', detail_div_new);
        div_article.insertAdjacentHTML('beforeend', article_div_new);
        div_price.insertAdjacentHTML('beforeend', price_div_new);
        div_carreta.insertAdjacentHTML('beforeend', carreta_div_new);
        div_amry.insertAdjacentHTML('beforeend', amry_div_new);
        div_armtek.insertAdjacentHTML('beforeend', armtek_div_new);
        div_emex.insertAdjacentHTML('beforeend', emex_div_new);
        div_avg_price.insertAdjacentHTML('beforeend', avg_div_new);
        div_change_price.insertAdjacentHTML('beforeend', change_div_new);

        console.log(`[message] Данные получены с сервера: ${event.data}`);
        // Получение всех цен из строки
        var carreta = "carreta_" + message.article;
        var amry = "amry_" + message.article;
        var armtek = "armtek_" + message.article;
        const carreta_div = document.getElementById(carreta);
        const amry_div = document.getElementById(amry);
        const armtek_div = document.getElementById(armtek);

        if (carreta_div != null) {
            var carreta_price = parseFloat(carreta_div.innerText);
        } else {
            var carreta_price = parseFloat(100000.12);
        }

        if (amry_div != null) {
            var amry_price = parseFloat(amry_div.innerText);
        } else {
            var amry_price = parseFloat(100000.12);
        }

        if (armtek_div != null) {
            var armtek_price = parseFloat(armtek_div.innerText);
        } else {
            var armtek_price = parseFloat(100000.12);
        }
        // *


        // Выбор минимальной цены
        const min_price = Math.min.apply(null, [carreta_price, amry_price, armtek_price])

        if (min_price === amry_price) {
            amry_div.style.backgroundColor = "#5b752d";
            carreta_div.style.backgroundColor = "#313946";
            armtek_div.style.backgroundColor = "#313946";
        } else if (min_price === carreta_price) {
            amry_div.style.backgroundColor = "#313946";
            carreta_div.style.backgroundColor = "#5b752d";
            armtek_div.style.backgroundColor = "#313946";
        } else if (min_price === armtek_price) {
            amry_div.style.backgroundColor = "#313946";
            carreta_div.style.backgroundColor = "#313946";
            armtek_div.style.backgroundColor = "#5b752d";
        }
        // *

        // Расчет средней цены
        var avg_price = ((carreta_price + amry_price + armtek_price) / 3).toFixed(2);
        var round_avg = (round_avg = avg_price % 10) <= 5 ? (parseInt(avg_price / 10) + 5 / 10) * 10 : (Math.round(parseInt(avg_price / 10) + round_avg / 10)) * 10;
        const avg_div = document.getElementById("avg_" + message.article);
        avg_div.innerText = round_avg;
        window.price_avg[message.article] = round_avg;
        // *
    }

    window.socket.onclose = function (e) {
        console.log("[close] Соединение закрыто");
        alert("Переподключение WebSocket, подождите и повторите свои действия");
        setTimeout(function() {
            connect(false);
          }, 1000);
    };
}