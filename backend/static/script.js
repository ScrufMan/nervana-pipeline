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
        // element to scroll to
        const target = $('.results');

        // scroll to the element
        $('html, body').animate({
            scrollTop: target.offset().top
        }, 200);
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

let nextFieldIdx = 1;

function addSearchCondition() {

    const inputGroup = document.createElement("div");
    inputGroup.classList.add("input-group", "col-md-12", "mb-3");

    const prependDiv = document.createElement("div");
    prependDiv.classList.add("input-group-prepend");

    const button = document.createElement("button");
    button.classList.add("btn", "btn-outline-secondary");
    button.type = "button";
    button.onclick = button.onclick = () => {
        inputGroup.remove();
        nextFieldIdx--;
    };
    button.innerHTML = "–";

    const defaultInput = document.getElementById("search_terms-0");
    const input = defaultInput.cloneNode(true);
    input.removeAttribute("id");
    input.name = `search_terms-${nextFieldIdx}`; // indexing from 0

    const appendDiv = document.createElement("div");
    appendDiv.classList.add("input-group-append");

    const defaultSelect = document.getElementById("entity_types-0");
    const select = defaultSelect.cloneNode(true);
    select.removeAttribute("id");
    select.name = `entity_types-${nextFieldIdx}`;

    prependDiv.appendChild(button);
    appendDiv.appendChild(select);
    inputGroup.appendChild(prependDiv);
    inputGroup.appendChild(input);
    inputGroup.appendChild(appendDiv);

    const additionalSearchConditions = document.getElementById("additional-search-conditions");
    additionalSearchConditions.appendChild(inputGroup);

    nextFieldIdx++;
}