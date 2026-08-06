const cards = document.querySelectorAll(".furniture-card");
const canvas = document.getElementById("roomCanvas");
const saveButton = document.getElementById("saveButton");

let selectedFurniture = null;

// ======================
// Выбор мебели
// ======================

cards.forEach(card => {

    card.addEventListener("dragstart", () => {

        selectedFurniture = {

            id: card.dataset.id,

            name: card.dataset.name

        };

    });

});

// ======================
// Разрешаем Drop
// ======================

canvas.addEventListener("dragover", (e) => {

    e.preventDefault();

});

// ======================
// Добавление мебели
// ======================

canvas.addEventListener("drop", (e) => {

    e.preventDefault();

    if (!selectedFurniture) return;

    const rect = canvas.getBoundingClientRect();

    const item = document.createElement("div");

    item.className = "furniture-item";

    item.dataset.id = selectedFurniture.id;

    item.innerText = selectedFurniture.name;

    item.style.left = (e.clientX - rect.left - 50) + "px";

    item.style.top = (e.clientY - rect.top - 35) + "px";

    canvas.appendChild(item);

    makeDraggable(item);

});

// ======================
// Перемещение мебели
// ======================

function makeDraggable(item) {

    let isDragging = false;

    let offsetX = 0;

    let offsetY = 0;

    item.addEventListener("mousedown", (e) => {

        isDragging = true;

        offsetX = e.offsetX;

        offsetY = e.offsetY;

    });

    document.addEventListener("mouseup", () => {

        isDragging = false;

    });

    document.addEventListener("mousemove", (e) => {

        if (!isDragging) return;

        const rect = canvas.getBoundingClientRect();

        let x = e.clientX - rect.left - offsetX;

        let y = e.clientY - rect.top - offsetY;

        x = Math.max(0, Math.min(x, canvas.clientWidth - item.offsetWidth));
        y = Math.max(0, Math.min(y, canvas.clientHeight - item.offsetHeight));

        item.style.left = x + "px";
        item.style.top = y + "px";

    });

}

// ======================
// Сохранение
// ======================

saveButton.addEventListener("click", () => {

    const furniture = [];

    document.querySelectorAll(".furniture-item").forEach(item => {

        furniture.push({

            furniture_id: item.dataset.id,

            x: parseInt(item.style.left),

            y: parseInt(item.style.top),

            rotation: 0

        });

    });

    fetch(

        "/planner/" + canvas.dataset.project + "/save/",

        {

            method: "POST",

            headers: {

                "Content-Type": "application/json",

                "X-CSRFToken": getCookie("csrftoken")

            },

            body: JSON.stringify(furniture)

        }

    )

    .then(response => response.json())

    .then(data => {

        alert("✅ Проект успешно сохранён!");

        console.log(data);

    })

    .catch(error => {

        console.error(error);

        alert("❌ Ошибка сохранения");

    });

});

// ======================
// Получение CSRF
// ======================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

                break;

            }

        }

    }

    return cookieValue;

}