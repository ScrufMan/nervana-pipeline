$(document).ready(function () {
    $('#search-form').submit(function (event) {
        event.preventDefault();
        const formData = $(this).serialize();
        const searchUrl = "/search"
        loadResults(formData, searchUrl);
    });

    $(document).on('click', '.page-link', function (event) {
        if ($(this).parent().hasClass("active")) {
            return
        }
        event.preventDefault();
        const formData = $('#search-form').serialize();
        const pageUrl = $(this).attr('href');
        loadResults(formData, pageUrl);
        // get the element you want to scroll to
        const target = $('.results');

        // scroll to the element
        $('html, body').animate({
            scrollTop: target.offset().top
        }, 200); // 1000 is the duration of the animation in milliseconds
    });
});

function loadResults(formData, url) {
    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        success: function (data) {
            $('.results').html(data.results);
        },
        error: function () {
            alert('Error loading results.');
        }
    });
}

function addSearchCondition() {
    const inputGroup = document.createElement("div");
    inputGroup.classList.add("input-group", "mt-2");

    const prependDiv = document.createElement("div");
    prependDiv.classList.add("input-group-prepend");

    const button = document.createElement("button");
    button.classList.add("btn", "btn-outline-secondary");
    button.type = "button";
    button.onclick = function () {
        inputGroup.remove();
    };
    button.innerHTML = "–";

    const input = document.createElement("input");
    input.type = "text";
    input.classList.add("form-control");
    input.placeholder = "Přidat další podmínku vyhledávání";

    const appendDiv = document.createElement("div");
    appendDiv.classList.add("input-group-append");

    const select = document.createElement("select");
    select.classList.add("custom-select");
    select.id = "additional-condition-type";
    let option = document.createElement("option");
    option.selected = true;
    option.innerHTML = "Všechny";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Telefonní číslo";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Emailová adresa";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Datum";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Souřadnice";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Číslo účtu";
    select.appendChild(option);
    option = document.createElement("option");
    option.innerHTML = "Jazyk";
    select.appendChild(option);

    prependDiv.appendChild(button);
    appendDiv.appendChild(select);
    inputGroup.appendChild(prependDiv);
    inputGroup.appendChild(input);
    inputGroup.appendChild(appendDiv);

    const additionalSearchConditions = document.getElementById("additional-search-conditions");
    additionalSearchConditions.appendChild(inputGroup);
}