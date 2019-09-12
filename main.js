$(function(){
    let levenshtein = require('leven');
    let autocomplete = require('autocompleter');

    let journals = require('./data/journals');
    let journalsList = Object.keys(journals);
    let providers = require('./data/providers');

    /* autocomplete journal */
    function compareLev(src, a, b) {
        return (levenshtein(a.toLowerCase(), src) / a.length) - (levenshtein(b.toLowerCase(), src) / b.length);
    }

    let journalInput = document.getElementById('input-journal');

    autocomplete({
        input: journalInput,
        fetch: (text, update) => {
            journalsList.sort((a, b) => compareLev(text, a, b));

            let suggs = [];
            journalsList.slice(0, 5).forEach(el => {
               suggs.push({label: el, value: el})
            });
            update(suggs);
        },
        onSelect: item => {
            journalInput.value = item.label;
        }
    });

    /* go to! */
    function flash_error(msg) {
        let $place = $('#flash-messages');
        $place.css('display', 'block');
        $place.children('.content').html(msg);
    }

    function goto_citation(journal, volume, page) {
        // check inputs
        if (journal.length == 0) {
            flash_error('Journal cannot be empty!');
            return;
        } else if (!(journal in journals)) {
            flash_error('Unknown journal');
            return;
        }

        let isNum = /[0-9]*/i;

        if (volume.length == 0) {
            flash_error('Volume cannot be empty');
            return;
        } else if (!isNum.test(volume)) {
            flash_error('Volume should be an integer');
            return;
        }

        if (page.length == 0) {
            flash_error('Page cannot be empty');
            return;
        } else if (!isNum.test(page)) {
            flash_error('Page should be an integer');
            return;
        }

        // ok, then!
        let journal_info = journals[journal];
        if (!(journal_info[0] in providers)) {
            flash_error('Even though journal is correct, there is no valid provider associated!?!');
            return;
        }

        if (journal_info[1] != null) { // correct internal abbreviation for this journal
            journal = journal_info[1];
        }

        let provider = providers[journal_info[0]];

        if(provider['method'] == 'GET') {
            window.open(provider['action'](journal, volume, page), '_blank');
        } else {
            flash_error('POST not yet implemented');
        }
    }

    $('#input-submit').click(function (event) {
        goto_citation($('#input-journal').val(), $('#input-volume').val(), $('#input-page').val());
    })
});

