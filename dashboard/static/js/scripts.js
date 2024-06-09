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
buttons.forEach(function(button) {
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
decreaseButtons.forEach(function(img) {
    img.parentElement.addEventListener('click', decreaseFilterNumber);
});

var increaseButtons = document.querySelectorAll('.btnPlusMinus img[src="/static/img/plus.svg"]');
increaseButtons.forEach(function(img) {
    img.parentElement.addEventListener('click', increaseFilterNumber);
});


function resetFilters() {
    // Находим все поля ввода и обнуляем их значения
    var filterInputs = document.querySelectorAll('.filterNumber');
    filterInputs.forEach(function(input) {
        input.value = 0;
    });

    // Скрываем все элементы с классом 'filterCheck'
    var filterChecks = document.querySelectorAll('.filterCheck');
    filterChecks.forEach(function(filterCheck) {
        filterCheck.style.display = 'none';
    });

    // Показываем все элементы с классом 'nameText'
    var nameTexts = document.querySelectorAll('.nameText');
    nameTexts.forEach(function(nameText) {
        nameText.style.display = 'block';
    });

    // Сбрасываем изображения на исходные (если нужно)
    var filterButtons = document.querySelectorAll('.filter img');
    filterButtons.forEach(function(img) {
        img.src = 'static/img/gala--settings.svg';
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
    checkboxes.forEach(function(checkbox) {
        var filterCheck = checkbox.querySelector('.filterCheck');
        var nameText = checkbox.querySelector('.nameText');
        var filterNumber = checkbox.querySelector('.filterNumber');
        var itemTextes = checkbox.querySelectorAll('.itemText');

        if (filterCheck && filterCheck.style.display === 'flex' && filterNumber) {
            // Получаем процент из фильтра
            var percentage = parseFloat(filterNumber.value);

            // Преобразуем значение в ячейке itemText в число и умножаем на (1 + процент/100)
            itemTextes.forEach(function(itemText) {
                var currentPrice = parseFloat(itemText.textContent);
                var newPrice = currentPrice * (1 + percentage / 100);

                // Обновляем значение в ячейке itemText
                itemText.textContent = newPrice.toFixed(2); // округляем до двух знаков после запятой
            });
            // Сбрасываем значение фильтра
            filterNumber.value = 0;

            // Сворачиваем фильтр и отображаем название колонки
            filterCheck.style.display = 'none';
            nameText.style.display = 'block';
        }
    });

    // Сбрасываем изображения на исходные
    var filterButtons = document.querySelectorAll('.filter img');
    filterButtons.forEach(function(img) {
        img.src = 'static/img/gala--settings.svg'; // путь к исходному изображению
    });
}

// Назначаем обработчик события для кнопки "Применить фильтры"
var applyButton = document.querySelector('.buttons .btn:nth-child(3)'); // предположительно, это третья кнопка в .buttons
if (applyButton) {
    applyButton.addEventListener('click', applyFilters);
}



