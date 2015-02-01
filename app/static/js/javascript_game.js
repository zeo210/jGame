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

Reveal.addEventListener( 'slidechanged', function( event ) {
    if(event.indexh == 0) {

    }
    else if(event.indexh == 1){
        var ele = document.getElementsByName("answer");
        for(var i=0;i<ele.length;i++)
            ele[i].checked = false;

        $.getJSON($SCRIPT_ROOT + '/_page1', {},
            function(data) {
                $("#page1_category").text(data.category);
            });
        return false;
    }
    else if(event.indexh == 2){
        $.getJSON($SCRIPT_ROOT + '/_page2', {},
            function(data) {
                $("#page2_category").text(data.category);
                $("#page2_clue").text(data.clue);
                $("#page2_answer1").text(data.answer1);
                $("#page2_answer2").text(data.answer2);
                $("#page2_answer3").text(data.answer3);
            });
        return false;
    }
    else if(event.indexh == 3){
        $.getJSON($SCRIPT_ROOT + '/_page3', {},
            function(data) {
                $("#page3_answer").text(data.answer);
            });
        return false;
    }
    else if(event.indexh == 4){
        $.getJSON($SCRIPT_ROOT + '/_page4', {},
            function(data) {
                $("#page4_answer").text(data.answer);
            });
        return false;
    }
});