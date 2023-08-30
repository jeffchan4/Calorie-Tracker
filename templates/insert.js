document.addEventListener('DOMContentLoaded', function() {
    const foodList = document.getElementById('cart1');
    const insertButton = document.getElementById('insertButton');
    

    insertButton.addEventListener('click', function() {
        const allFood = [];

        // Loop through the list items to collect all items
        const listItems = foodList.getElementsByTagName('li');
        for (let i = 0; i < listItems.length; i++) {
            const food = listItems[i].textContent;
            allFood.push(food);
        }

        // Send all data to the server using AJAX
        if (allFood.length > 0) {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/insert_food_table', true);
            xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    message.textContent = xhr.responseText;
                }
            };
            xhr.send(JSON.stringify(allFood));
        }
    });
});
