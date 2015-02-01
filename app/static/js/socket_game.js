Reveal.initialize({
    controls: false,
    loop: true,
    touch: false,
    keyboard: false,
    autoSlideStoppable: true,
    transitionSpeed: 'fast',
    progress: false
});


var milisec=0;
var seconds=0;
document.timer.display.value='0.0';

function update_timer(){
    if (milisec<=0){
        milisec=9;
        seconds-=1;
    }

    if (seconds<=-1){
        milisec=0;
        seconds+=1;
    }
    else
        milisec-=1;
    document.timer.display.value=seconds+"."+milisec;
    setTimeout("update_timer()",100);
}


$(document).ready(function(){
    var namespace = '/_socket';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);


    socket.on('starting page', function (msg) {
        if(Reveal.getIndices().h == 0) {
            Reveal.right();
        }
    });

    socket.on('category and value page', function (msg) {
        if(Reveal.getIndices().h == 1) {
            $("#category_page2").text(msg.category);
            $("#category_page3").text(msg.category);
            Reveal.right();
        }
    });

    socket.on('select answer page', function (msg) {
        if(Reveal.getIndices().h == 2) {
            $("#clue_page3").text(msg.clue);
            $("#answer1_page3").text(msg.answer1);
            $("#answer2_page3").text(msg.answer2);
            $("#answer3_page3").text(msg.answer3);
            Reveal.right();
        }
    });

    socket.on('show answer page', function (msg) {
        if(Reveal.getIndices().h == 3) {
            socket.emit('selected_answer', $('input[name=answer]:checked', 'form#answer').val());
            $("#answer_page4").text(msg.answer);
            $("#answer_page5").text(msg.answer);
            Reveal.right();
        }
    });

    socket.on('result page', function (msg) {
        if(Reveal.getIndices().h == 4) {
            Reveal.right();
        }
    });

    socket.on('next round page', function (msg) {
        var index = Reveal.getIndices().h;
        if(index == 5) {
            Reveal.right();
        }
        else {
            Reveal.slide(0,0,0);
        }
        var ele = document.getElementsByName("answer");
        for(var i=0;i<ele.length;i++)
                ele[i].checked = false;
        $("#answer_page5").removeAttr("style");
        $("#results").empty();
    });

    socket.on('answer response', function (msg) {
        if(msg['check']){
            $("#answer_page5").css("color", "green");
        }
        else {
            $("#answer_page5").css("color", "red");
        }
    });

    socket.on('result response', function (msg) {
        $("table#results").append("<tr><td>" + msg['check'] + "</td><td>checking</td><td>more data</td></tr>")
    });
});