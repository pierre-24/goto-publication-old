const $ = require("jquery");

$(function(){
    "use strict";
    const autocomplete = require("autocompleter");

    function flashError(msg) {
        let $place = $("#flash-messages");
        $place.css("display", "block");
        $place.children(".content").html(msg);
        $place.children(".close").click(() => $place.css("display", "none"));
    }

    let journalInput = document.getElementById("input-journal");

    autocomplete({
        input: journalInput,
        fetch: (text, update) => {
            $.ajax({
                url: "/api/suggests?q=" + text,
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

    function gotoCitation(journal, volume, page) {
        $("#flash-messages").css("display", "none");
        let v = $submit.val();
        $submit.attr("disabled", "disabled").val("requesting");

        $.ajax({
            url: "/api/url?journal="+ journal + "&volume=" + volume + "&page=" + page,
            success: a => {
                if ("url" in a)
                    window.open(a.url, "_blank");
                $submit.removeAttr("disabled").val(v);
            },
            error: (xhr) => {
                flashError(Object.values(xhr.responseJSON.message));
                $submit.removeAttr("disabled").val(v);
            }
        });
    }

    $submit.click(() => {
        gotoCitation($("#input-journal").val(), $("#input-volume").val(), $("#input-page").val());
    });
});

