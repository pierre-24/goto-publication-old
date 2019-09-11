$(function(){
    let levenshtein = require('leven');

    let journals = {};
    let journalsList = [];
    let providers = {};

    let gotJournals = false;
    let gotProviders = false;

    function setup() {
        $.getJSON('./data/journals.json', function (data) {
            journals = data;
            journalsList = Object.keys(data);
            gotJournals = true;
        });

        $.getJSON('./data/providers.json', function (data) {
            providers = data;
            gotProviders = true;
        });
    }

    function compareLev(src, a, b) {
        return (levenshtein(a.toLowerCase(), src) / a.length) - (levenshtein(b.toLowerCase(), src) / b.length);
    }

    $('#input-journal').keyup(function (input) {
        if (gotJournals) {
            let value = $(this).val().toLowerCase();

            journalsList.sort(function (a, b) { return compareLev(value, a, b) });
            console.log(journalsList);
        }
    });

    setup();
});

