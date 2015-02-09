// Full list of configuration options available at:
// https://github.com/hakimel/reveal.js#configuration
Reveal.initialize({
    controls: false,
    loop: true,
    touch: false,
    keyboard: false,
    autoSlideStoppable: true,
    transitionSpeed: 'fast',
    progress: false
});

$("#check_answer").click(function() {
    $("input[name='answer']:checked").each(function() {
        var idVal = $(this).attr("id");
        var grabbed_text = $("label[for='"+idVal+"']").text().trim();
        $("#repeat_answer_page4").text(grabbed_text);
        if ($("#answer_page4").text().trim() == grabbed_text) {
            $("#repeat_answer_page4").css("color", "green");
        }
        else if (grabbed_text != "") {
            $("#repeat_answer_page4").css("color", "red");
        }
    });
    Reveal.right();
});

$("#next_question").click(function() {
    $.getJSON($SCRIPT_ROOT + '/_nextQuestion', {},
            function(data) {
                var ele = document.getElementsByName("answer");
                for(var i=0;i<ele.length;i++)
                        ele[i].checked = false;
                $("#category_page3").text(data.category);
                $("#clue_page3").text(data.clue);
                $("#answer1_page3").text(data.selectable_answers[0]);
                $("#answer2_page3").text(data.selectable_answers[1]);
                $("#answer3_page3").text(data.selectable_answers[2]);
                Reveal.left();
                setTimeout(function(){
                    $("#answer_page4").text(data.answer);
                    $("#repeat_answer_page4").text("* No Answer *").removeAttr("style");
                }, 800);
            });
});


$(document).ready(function(){
    Reveal.slide(3,0,0);
});