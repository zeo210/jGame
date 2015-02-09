Reveal.initialize({
    controls: false,
    loop: true,
    touch: false,
    keyboard: false,
    autoSlideStoppable: true,
    transitionSpeed: 'fast',
    progress: false
});


var timerInterval = null;
var milisec=0;
var seconds=0;
document.timer.display.value='0.0';


update_timer = function(){
    if (milisec<=0){
        milisec=9;
        seconds-=1;
    }

    if (seconds<=-1){
        milisec=0;
        seconds=0;
        clearInterval(timerInterval);
    }
    else
        milisec-=1;
    document.timer.display.value=seconds+"."+milisec;
};


function start_timer(seconds_input, milisec_input){
    clearInterval(timerInterval);

    seconds = seconds_input;
    milisec = milisec_input;
    document.timer.display.value=seconds+"."+milisec;

    timerInterval = setInterval(update_timer, 100);
}


$(document).ready(function(){
    var namespace = '/_socket';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);


    socket.on('starting page', function () {
        if(Reveal.getIndices().h == 0) {
            start_timer(3,0);
            Reveal.right();
        }
    });

    socket.on('category and value page', function (msg) {
        if(Reveal.getIndices().h == 1) {
            if(mode != "display")
                socket.emit('max_wager');
            $('#wager').val("0");
            $('#wager_output').val("0");
            $("#category_page2").text(msg.category);
            $("#category_page3").text(msg.category);
            start_timer(10,0);
            Reveal.right();
        }
    });

    socket.on('select answer page', function (msg) {
        if(Reveal.getIndices().h == 2) {
            $("#clue_page3").text(msg.clue);
            $("#answer1_page3").text(msg.answer1);
            $("#answer2_page3").text(msg.answer2);
            $("#answer3_page3").text(msg.answer3);
            start_timer(10,0);
            Reveal.right();
            if(mode != "display")
                socket.emit('wagered_amount', $('input[name=wager_input]').val());
        }
    });

    socket.on('show answer page', function (msg) {
        if(Reveal.getIndices().h == 3) {
            if(mode != "display")
                socket.emit('selected_answer', $('input[name=answer]:checked', 'form#answer').val());
            $("input[name='answer']:checked").each(function() {
                var idVal = $(this).attr("id");
                var grabbed_text = $("label[for='" + idVal + "']").text().trim();
                $("#repeat_answer_page5").text(grabbed_text);
            });
            $("#answer_page4").text(msg.answer);
            $("#answer_page5").text(msg.answer);
            start_timer(3,0);
            Reveal.right();
        }
    });

    socket.on('result page', function (msg) {
        if(Reveal.getIndices().h == 4) {
            start_timer(10,0);
            Reveal.right();
            console.log(msg.total_difference);
            total_difference = msg.total_difference;
            if (msg.total_difference > 0)
                $("#point_difference").text("+" + total_difference);
            else
                $("#point_difference").text(total_difference);
        }
    });

    socket.on('next round page', function (msg) {
        var index = Reveal.getIndices().h;
        start_timer(3,0);
        if(index == 5) {
            Reveal.right();
        }
        else {
            Reveal.slide(0,0,0);
        }
        var ele = document.getElementsByName("answer");
        for(var i=0;i<ele.length;i++)
                ele[i].checked = false;
        $("#repeat_answer_page5").removeAttr("style");
        $("#repeat_answer_page5").text("");
        $("#results").empty();
    });

    socket.on('answer response', function (msg) {
        if(msg.check){
            $("#repeat_answer_page5").css("color", "green");
        }
        else {
            $("#repeat_answer_page5").css("color", "red");
        }
        console.log(msg.current_amount);
        $("#user_amount").text(msg.current_amount);
    });

    socket.on('max wager response', function (msg){
        $("#wager").attr('max', msg.max_wager);
    });

    socket.on('wager amount response', function (msg){
        alert(msg);
    });

    if(mode != "display")
        socket.emit('max_wager');
});