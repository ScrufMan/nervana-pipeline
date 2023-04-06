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
    // Creating a new row element with classes "form-row", "justify-content-between", and "align-items-center"
    const row = $('<div></div>').addClass('form-row justify-content-between align-items-center');

    // Creating a new search group element with classes "input-group" and "col-md-7"
    const searchGroup = $('<div></div>').addClass('input-group col-md-7');

    // Creating a new prepend div element with classes "input-group-prepend" and "d-block"
    const prependDiv = $('<div></div>').addClass('input-group-prepend d-block');

    // Creating a new button element with classes "btn" and "btn-outline-secondary", setting its type to "button", and adding an onclick event handler
    const button = $('<button></button>').addClass('btn btn-outline-secondary').attr('type', 'button').click(() => {
        row.remove();
        nextFieldIdx--;
    }).html('–');

    // Getting the default input element with id "search_terms-0", cloning it, and modifying its attributes
    const input = $('#search_terms-0').clone().removeAttr('style').attr({
        'name': `search_terms-${nextFieldIdx}`,
        'id': `search_terms-${nextFieldIdx}`,
        'value': '',
    }).addClass('rounded-right');

    // Getting the default entity types group element with id "entityTypesGroup", cloning it, and modifying its attributes
    const entityTypesGroup = $('#entityTypesGroup').clone().removeClass('mt-3');

    // Adding event listeners to the entity types group's dropdown-menu and check-all elements
    entityTypesGroup.find('.dropdown-menu').on('click', function (e) {
        e.stopPropagation();
    });
    entityTypesGroup.find('.check-all').on('click', function () {
        const previousSibling = $(this).parent().prev();
        previousSibling.find('input[type="checkbox"]').prop('checked', true);
    });

    // Adding an event listener to all elements with the class .uncheck-all
    entityTypesGroup.find('.uncheck-all').on('click', function () {
        const previousSibling = $(this).parent().prev();
        previousSibling.find('input[type="checkbox"]').prop('checked', false);
    });

    // Modifying the cloned entity types group's input elements' attributes
    entityTypesGroup.find('input').each(function () {
        const name = $(this).attr('name');
        const id = $(this).attr('id');
        const newName = name.replace(/entity_types_list-\d+/g, `entity_types_list-${nextFieldIdx}`);
        const newId = id.replace(/entity_types_list-\d+-(\d+)/g, `entity_types_list-${nextFieldIdx}-$1`);
        $(this).attr('name', newName).attr('id', newId);

        const label = $(this).next('label');
        label.attr('for', newId);
    });

    // Appending the button and input elements to the search group element, and then appending the search group and entity types group elements to the row element
    prependDiv.append(button);
    searchGroup.append(prependDiv, input);
    row.append(searchGroup, entityTypesGroup);

    // Appending the row element to the "additional-search-conditions" element and incrementing the "nextFieldIdx" variable
    $('#additional-search-conditions').append(row);
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
