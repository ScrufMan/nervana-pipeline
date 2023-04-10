$(document).ready(function () {
    // don't close dropdown menu when clicking indise it
    $(document).on('click', '.dropdown-menu', function (event) {
        event.stopPropagation();
    });

    // When check-all button is clicked, check all checkboxes in dropdown menu
    $(document).on('click', '.check-all', function () {
        const dropdown = $(this).parent().parent();
        dropdown.find('input[type="checkbox"]').prop('checked', true);
    });

    // When ucheck-all button is clicked, uncheck all checkboxes in dropdown menu
    $(document).on('click', '.uncheck-all', function () {
        const dropdown = $(this).parent().parent();
        dropdown.find('input[type="checkbox"]').prop('checked', false);
    });

    // Preserve form data when modifying form until form is submitted
    let originalFormData;

    // When the search form is submitted, send an AJAX request to the server
    $('#search-form').submit(function (event) {
        event.preventDefault();
        originalFormData = $(this).serialize();
        const searchUrl = '/search'
        loadResults(originalFormData, searchUrl);
    });

    $(document).on('click', '.page-link', function (event) {
        if ($(this).parent().hasClass('active')) {
            return
        }
        event.preventDefault();
        // send form as it was submitted
        const formData = originalFormData;
        const pageUrl = $(this).attr('href');

        const resultsDiv = $('.results');

        resultsDiv.fadeOut(200)
        loadResults(formData, pageUrl);
        resultsDiv.fadeIn(200)

        // scroll to the results div after the page has loaded
        $('html, body').animate({
            scrollTop: resultsDiv.offset().top
        }, 200);
    });

    $(document).on('click', '#export-csv', function () {
        if (originalFormData) {
            downloadCSV(originalFormData);
        } else {
            alert('Something went wrong with form data.');
        }
    });

    // Function for handling modal search
    let currentIndex = 0;
    let matches = [];

     // Scroll to the currently matched item
    function scrollToMatch(index) {
        if (matches.length > 0) {
            const position = matches[index];
            $('.search-match').removeClass('search-match-current'); // Deselect previous match
            matches[index].element.addClass('search-match-current'); // Highlight the current match

            $('.modal-body').scrollTop(position.top); // Scroll to the current match position
        }
    }

    // Escape special characters in the search string for use in a RegExp
    function escapeRegExp(string) {
        return string.replace(/[.*+\-?^${}()|[\]\\]/g, '\\$&');
    }

    // Reset search variables when the modal is shown
    $('#file-contents-modal').on('show.bs.modal', function () {
        currentIndex = 0;
        matches = [];
        $('#modal-search-input').val('');
        $('#modal-search-info').text('');
    });

    // Handle search input changes
    $('#modal-search-input').on('keyup', function () {
        currentIndex = 0;
        let searchText = $(this).val().toLowerCase();

        // Remove the highlight from the previous match
        $('.search-match-current').removeClass('search-match-current');

        // Update the content of the preformatted text element with new matches
        $('#file-contents-pre').html(function (_, htmlContent) {
            // Remove old matches
            htmlContent = htmlContent.replace(/<mark class="search-match(?:-current)?">([\s\S]*?)<\/mark>/gi, '$1');

            // Highlight new matches
            if (searchText !== '') {
                const regex = new RegExp('(' + escapeRegExp(searchText) + ')', 'gi');
                matches = [];
                htmlContent = htmlContent.replace(regex, function (match) {
                    matches.push({match: match, index: matches.length});
                    return '<mark class="search-match">' + match + '</mark>';
                });
                $('#modal-search-info').text(matches.length > 0 ? `${currentIndex + 1} z ${matches.length}` : '');
            } else {
                $('#modal-search-info').text(''); // Clear search info text when search field is empty
            }
            return htmlContent;
        });

        // Update the matches array with new match elements and positions
        matches = [];
        $('.search-match').each(function (index) {
            matches.push({match: $(this).text(), index: index, top: $(this).position().top, element: $(this)});
        });

        // Scroll to the first match
        scrollToMatch(currentIndex);
    });

    // Handle "Next" button click
    $('#modal-search-next').on('click', function () {
        if (matches.length > 0) {
            currentIndex = (currentIndex + 1) % matches.length;
            scrollToMatch(currentIndex);
            $('#modal-search-info').text(`${currentIndex + 1} z ${matches.length}`);
        }
    });

    // Handle "Previous" button click
    $('#modal-search-prev').on('click', function () {
        if (matches.length > 0) {
            currentIndex = (currentIndex - 1 + matches.length) % matches.length;
            scrollToMatch(currentIndex);
            $('#modal-search-info').text(`${currentIndex + 1} z ${matches.length}`);
        }
    });

    // Handle "Scroll to Top" button click
    $('#modal-scroll-to-top').on('click', function () {
        $('.modal-body').animate({scrollTop: 0}, 500);
    });
});


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

let nextFieldIdx = 1;

function addSearchCondition() {
    // Creating a new row element with classes "form-row", "justify-content-between", and "align-items-center"
    const row = $('<div></div>').addClass('form-row justify-content-between align-items-center');

    // Creating a new search group element with classes "input-group" and "col-md-7"
    const searchGroup = $('<div></div>').addClass('input-group col-md-7');

    // Creating a new prepend div element with classes "input-group-prepend" and "d-block"
    const prependDiv = $('<div></div>').addClass('input-group-prepend d-block');

    const button = $('<button></button>').addClass('btn btn-outline-secondary').attr('type', 'button').click(() => {
        row.remove();
        nextFieldIdx--;
    }).html('–');

    // Getting the default input element with id "search_terms-0", cloning it, and modifying its attributes
    const input = $('#search_terms-0').clone().val('').removeAttr('style').attr({
        'name': `search_terms-${nextFieldIdx}`,
        'id': `search_terms-${nextFieldIdx}`,
    }).addClass('rounded-right');

    // Getting the default entity types group element with id "entityTypesGroup", cloning it, and modifying its attributes
    const entityTypesGroup = $('#entityTypesGroup').clone().removeClass('mt-3');

    // Modifying the cloned entity types group's input elements' attributes
    entityTypesGroup.find('input').each(function () {
        $(this).prop('checked', true);
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
                        $('#file-contents-pre').text(response.plaintext);
                        $('#file-contents-modal').modal('show');
                    }
                });
            });
        },
        error: function () {
            alert('Error loading results.');
        }
    });
}

// Function to download the CSV file
function downloadCSV(formData) {
    fetch('/export-csv', {
        method: 'POST',
        body: formData,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'results.csv';
            a.click();
        });
}

