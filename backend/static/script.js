$(document).ready(function () {
    // don't close dropdown menu when clicking on label
    $('.dropdown-menu').on('click', function (e) {
        e.stopPropagation();
    });

    $('#check-all').click(function () {
        $('input[name=\'entity_types\']').prop('checked', true);
    });

    $('#uncheck-all').click(function () {
        $('input[name=\'entity_types\']').prop('checked', false);
    });

    let originalFormData;
    $('#search-form').submit(function (event) {
        event.preventDefault();
        const formData = $(this).serialize();
        originalFormData = $('#search-form').serialize();
        const searchUrl = '/search'
        loadResults(formData, searchUrl);
    });

    $(document).on('click', '.page-link', function (event) {
        if ($(this).parent().hasClass('active')) {
            return
        }
        event.preventDefault();
        // send form as it was submitted
        const formData = originalFormData;
        const pageUrl = $(this).attr('href');

        $('.results').fadeOut(200)
        loadResults(formData, pageUrl);
        $('.results').fadeIn(200)
        // element to scroll to
        const target = $('.results');


        $('#search-form').se;
        // scroll to the element
        $('html, body').animate({
            scrollTop: target.offset().top
        }, 200);
    });
});

let nextFieldIdx = 1;

function addSearchCondition() {

    const inputGroup = document.createElement('div');
    inputGroup.classList.add('input-group', 'col-md-9', 'mb-3');

    const prependDiv = document.createElement('div');
    prependDiv.classList.add('input-group-prepend');

    const button = document.createElement('button');
    button.classList.add('btn', 'btn-outline-secondary');
    button.type = 'button';
    button.onclick = button.onclick = () => {
        inputGroup.remove();
        nextFieldIdx--;
    };
    button.innerHTML = '–';

    const defaultInput = document.getElementById('search_terms-0');
    const input = defaultInput.cloneNode(true);
    input.removeAttribute('id');
    input.name = `search_terms-${nextFieldIdx}`;
    input.value = '';

    const appendDiv = document.createElement('div');
    appendDiv.classList.add('input-group-append');

    prependDiv.appendChild(button);
    inputGroup.appendChild(prependDiv);
    inputGroup.appendChild(input);
    inputGroup.appendChild(appendDiv);

    const additionalSearchConditions = document.getElementById('additional-search-conditions');
    additionalSearchConditions.appendChild(inputGroup);

    nextFieldIdx++;
}

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

function checkSearchTerm(input) {
    // Get the input value
    let value = input.value;

    // Check the value and set the background color accordingly
    if (value.startsWith('r:')) {
        // Get the regular expression entered after "r:"
        let regexStr = value.substring(2);

        // Lint the regular expression
        try {
            let regex = new RegExp(regexStr);
            input.style.backgroundColor = '#9ef7aa';
            input.setCustomValidity('');
        } catch (e) {
            input.style.backgroundColor = '#fc9f9f';
            input.setCustomValidity('Regulární výraz není správný');
        }
    } else if (value.startsWith('"') && value.endsWith('"')) {
        input.style.backgroundColor = '#fff79c';
    } else {
        input.style.backgroundColor = '';
    }
}
