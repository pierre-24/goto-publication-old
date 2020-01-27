const $ = require("jquery");

$(function(){
    "use strict";
    const autocomplete = require("autocompleter");
    const clipboardCopy = require("clipboard-copy");

    function displayIt($place) {
        $place.css("display", "block");
        let $l = $("<a href='#' class='close'>&cross;</a>");
        $l.click(() => $place.css("display", "none"));
        $place.prepend($l);
    }

    let helpsToDisplay = [
        [$("#input-journal"), "left"],
        [$("#input-suggs-source"), "left"],
        [$("#input-volume"), "left"],
        [$("#input-page"), "right"],
        [$("#input-action"), "right"],
        [$("#input-submit"), "right"]
    ];

    function displayHelpTooltip($msg, n) {
        if (n >= helpsToDisplay.length || n < 0) {
            $msg.css("display", "none");
        } else {
            $msg.css("display", "block");
            $msg.html("");
            let $elm = helpsToDisplay[n][0];
            let pos = $elm.offset();
            $msg.append($("<div class='content'></div>").html($elm.data("help")));

            let $l = $("<a href='#' class='close'>&cross;</a>");
            $l.click(() => displayHelpTooltip($msg, n + 1));
            $msg.prepend($l);
            $msg.append("<div class='arrow  arrow-" + helpsToDisplay[n][1] + "'> </div>");

            $msg.css({
                "left": pos.left - (helpsToDisplay[n][1] === "right" ? $msg.outerWidth(true) - $elm.outerWidth(): 0),
                "top": pos.top - $msg.outerHeight(),
            });
        }
    }

    function displayHelp() {
        let $p = $("#input-form");
        let $msg = $("#help-message");
        $p.append($msg);

        displayHelpTooltip($msg, 0);
    }

    $("#explainLink").click(() => displayHelp());

    function flashError(msg) {
        let $place = $("#flash-messages");
        $place.html("<p class='content'>" + msg + "</p>");
        displayIt($place);
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

