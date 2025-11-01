let activeFilter = "all"

function filterBusinesses(type, button) {
    var cards = document.getElementsByClassName('business');
    var buttons = document.getElementsByClassName('filter-btn');
    var i;

    // Toggle button highlight using Tailwind utility classes
    if (button.classList.contains('bg-indigo-600')) {
    // unhighlight and show all
    button.classList.remove('bg-indigo-600', 'text-white');
    button.classList.add('bg-gray-700');
    type = 'all';
    } else {
    // reset all buttons to default
    for (i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('bg-indigo-600', 'text-white');
        buttons[i].classList.add('bg-gray-700');
    }
    // highlight clicked one
    button.classList.remove('bg-gray-700');
    button.classList.add('bg-indigo-600', 'text-white');
    }

    // Filter cards
    for (i = 0; i < cards.length; i++) {
    var cardType = cards[i].getAttribute('data-type');
    if (type === 'all' || cardType === type) {
        cards[i].classList.remove('hidden');
    } else {
        cards[i].classList.add('hidden');
    }
    }

    activeFilter = type
}

function searchBusinesses() {
    var searchValue = document.getElementById('search-bar').value.toLowerCase();
    var cards = document.getElementsByClassName('business');
    var i;

    
    for (i = 0; i < cards.length; i++) {
        var buisnessName = cards[i].getElementsByClassName("buisness-name")[0].innerText.toLowerCase();
        var type = cards[i].getAttribute('data-type')

        console.log(activeFilter)
        console.log(type)

        if (buisnessName.indexOf(searchValue)==-1){
            cards[i].classList.add('hidden') 
        }else{

            if (type === activeFilter || activeFilter ==="all"){
                cards[i].classList.remove("hidden")
            }
            
        }
    }
}