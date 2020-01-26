const $ = require("jquery");

$(function(){
    "use strict";
    const autocomplete = require("autocompleter");
    const clipboardCopy = require("clipboard-copy");

    function flashThis($place) {
        $place.css("display", "block");
        $place.children(".close").click(() => $place.css("display", "none"));
    }

    $('#explainLink').click(() => flashThis($('#explain')));

    function flashError(msg) {
        let $place = $("#flash-messages");
        $place.children(".content").html(msg);
        flashThis($place);
    }

    let journalInput = document.getElementById("input-journal");

    autocomplete({
        input: journalInput,
        fetch: (text, update) => {
            $.ajax({
                url: "/api/suggests?q=" + text + "&source=" + $("#input-suggs-source").val(),
                success: a => {
                    if("suggestions" in a) {
                        let suggs = [];
                        a.suggestions.forEach(e => suggs.push({label: e, value: e}));
                        update(suggs);
                    }
                }
            });
        },
        onSelect: item => {
            journalInput.value = item.label;
        }
    });

    let $submit  = $("#input-submit");

    function addResult(journal, volume, page, output) {
        let $table = $("#table-results");

        if ($table.children().length === 0) // add headers
            $table.append("<tr id='table-results-headers'>" +
                "<th style='width: 16px'></th>" +
                "<th>Journal</th>" +
                "<th style='min-width: 5%'>vol.</th>" +
                "<th style='min-width: 5%'>pp.</th>" +
                "</tr>");

        let $heads = $("#table-results-headers");

        let $tr = $(
            "<tr><td><a href='"+ output.providerWebsite +"'>" +
            "<img class='icon' src='" + output.providerIcon + "' alt='" + output.providerName +"' title='" + output.providerName +"'>" +
            "</a></td>" +
            "<td>"+ journal +"</td><td>"+ volume +"</td><td>"+ page +"</td></tr>");

        let txt = "", link = "";

        if ("doi" in output) {
            txt = output.doi;
            link = output.url;
        } else {
            txt = link = output.url;
        }

        let $inp = $("<input type='text' value='"+ txt + "'>");

        let $copy = $("<button title='copy'><i class=\"far fa-clipboard\"></i></button>");
        $copy.click(() => clipboardCopy(txt));

        let $go = $("<button title='go!'><i class=\"fas fa-external-link-alt\"></i></button>");
        $go.click(() => window.open(link, "_blank"));

        $tr.append($("<td class='results'></td>").append($inp).append($copy).append($go)).insertAfter($heads);
    }

    function getIt(journal, volume, page, action) {
        $("#flash-messages").css("display", "none");
        let v = $submit.val();
        $submit.attr("disabled", "disabled").val("requesting");

        if (["url", "doi"].indexOf(action) < 0)
            return flashError("unknown action " + action);

        $.ajax({
            url: "/api/" + action + "?journal="+ journal + "&volume=" + volume + "&page=" + page,
            success: a => {
                if ("result" in a) {
                    addResult(journal, volume, page, a.result);
                    // window.open(a.url, "_blank");
                }
                $submit.removeAttr("disabled").val(v);
            },
            error: xhr => {
                flashError(Object.values(xhr.responseJSON.message));
                $submit.removeAttr("disabled").val(v);
            }
        });
    }

    $submit.click(() => {
        getIt($("#input-journal").val(), $("#input-volume").val(), $("#input-page").val(), $("#input-action").val());
    });
});

