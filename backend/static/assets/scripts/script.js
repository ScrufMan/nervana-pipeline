$(document).ready(function () {
    // don't close dropdown menu when clicking on label
    $('.dropdown-menu').on('click', function (e) {
        e.stopPropagation();
    });

    $('.check-all').on('click', function () {
        // Get the parent of the clicked element and its previous sibling
        const previousSibling = $(this).parent().prev();

        // For each input inside the previous sibling, set checked
        previousSibling.find('input[type="checkbox"]').prop('checked', true);
    });

    // Add a click event listener to all elements with the class .uncheck-all
    $('.uncheck-all').on('click', function () {
        // Get the parent of the clicked element and its previous sibling
        const previousSibling = $(this).parent().prev();

        // For each input inside the previous sibling, set unchecked
        previousSibling.find('input[type="checkbox"]').prop('checked', false);
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
    const row = document.createElement('div');
    row.classList.add('form-row');
    row.classList.add('justify-content-between');
    row.classList.add('align-items-center');

    const searchGroup = document.createElement('div');
    searchGroup.classList.add('input-group', 'col-md-7');

    const prependDiv = document.createElement('div');
    prependDiv.classList.add('input-group-prepend');
    prependDiv.classList.add('d-block');

    const button = document.createElement('button');
    button.classList.add('btn', 'btn-outline-secondary');
    button.type = 'button';
    button.onclick = button.onclick = () => {
        row.remove();
        nextFieldIdx--;
    };
    button.innerHTML = '–';

    const input = document.getElementById('search_terms-0').cloneNode(true);
    input.name = `search_terms-${nextFieldIdx}`;
    input.id = `search_terms-${nextFieldIdx}`;
    input.value = '';
    input.classList.add('rounded-right');
    input.removeAttribute('style');
    const entityTypesGroup = document.querySelector('#entityTypesGroup').cloneNode(true);

    entityTypesGroup.classList.remove('mt-3');

    $(entityTypesGroup).find('.dropdown-menu').on('click', function (e) {
        e.stopPropagation();
    });

    $(entityTypesGroup).find('.check-all').on('click', function () {
        // Get the parent of the clicked element and its previous sibling
        const previousSibling = $(this).parent().prev();

        // For each input inside the previous sibling, set checked
        previousSibling.find('input[type="checkbox"]').prop('checked', true);
    });

    // Add a click event listener to all elements with the class .uncheck-all
    $(entityTypesGroup).find('.uncheck-all').on('click', function () {
        // Get the parent of the clicked element and its previous sibling
        const previousSibling = $(this).parent().prev();

        // For each input inside the previous sibling, set unchecked
        previousSibling.find('input[type="checkbox"]').prop('checked', false);
    });

    const checkboxes = entityTypesGroup.querySelectorAll('input');

    checkboxes.forEach(checkbox => {
        const name = checkbox.getAttribute('name');
        const id = checkbox.getAttribute('id');
        const newName = name.replace(/entity_types_list-\d+/g, `entity_types_list-${nextFieldIdx}`);
        const newId = id.replace(/entity_types_list-\d+-(\d+)/g, `entity_types_list-${nextFieldIdx}-$1`);
        checkbox.setAttribute('name', newName);
        checkbox.setAttribute('id', newId);

        const label = checkbox.nextElementSibling;
        label.setAttribute('for', newId);
    });


    prependDiv.appendChild(button);
    searchGroup.appendChild(prependDiv);
    searchGroup.appendChild(input);

    row.appendChild(searchGroup);
    row.appendChild(entityTypesGroup);

    const additionalSearchConditions = document.getElementById('additional-search-conditions');

    additionalSearchConditions.appendChild(row);

    nextFieldIdx++;
}

function loadResults(formData, url) {
    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        success: function (data) {
            $('.results').html(data.results);
            $('.file-open-link').click(function (e) {
                e.preventDefault();
                $.ajax({
                    type: 'GET',
                    url: $(this).attr('href'),
                    success: function (response) {
                        $('.modal-title').text(response.path);
                        $('#file_contents_pre').text(response.plaintext);
                        $('#file_contents_modal').modal('show');
                    }
                });
            });
        },
        error: function () {
            alert('Error loading results.');
        }
    });
}

function checkSearchTerm(input) {
    // Get the input value
    let value = input.value;
    input.setCustomValidity('');
    // Check the value and set the background color accordingly
    if (value.startsWith('r:')) {
        // Get the regular expression entered after "r:"
        let regexStr = value.substring(2);

        // Lint the regular expression
        try {
            let regex = new RegExp(regexStr);
            input.style.backgroundColor = '#9ef7aa';
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
