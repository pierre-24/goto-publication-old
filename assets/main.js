'use strict';

const $ = require('jquery');

$(function(){
    const autocomplete = require('autocompleter');

    function flash_error(msg) {
        let $place = $('#flash-messages');
        $place.css('display', 'block');
        $place.children('.content').html(msg);
    }

    let journalInput = document.getElementById('input-journal');

    autocomplete({
        input: journalInput,
        fetch: (text, update) => {
            $.ajax({
                url: '/api/suggests?q=' + text,
                success: a => {
                    if('suggestions' in a) {
                        let suggs = [];
                        a['suggestions'].forEach(e => suggs.push({label: e, value: e}));
                        update(suggs);
                    }
                }
            });
        },
        onSelect: item => {
            journalInput.value = item.label;
        }
    });

    function goto_citation(journal, volume, page) {
        $('#flash-messages').css('display', 'none');

        $.ajax({
            url: '/api/url?journal='+ journal + '&volume=' + volume + '&page=' + page,
            success: a => {
                if ('url' in a)
                    window.open(a['url'], '_blank');
            },
            error: (xhr, status, error) => {
                flash_error(Object.values(xhr.responseJSON['message']))
            }
        });
    }

    $('#input-submit').click(function (event) {
        goto_citation($('#input-journal').val(), $('#input-volume').val(), $('#input-page').val());
    })
});

