URL = window.URL || window.webkitURL;

var gumStream;
var rec;
var input;

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext;


function getAudio(blob) {
    var xhr=new XMLHttpRequest();
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var res = JSON.parse(xhr.responseText);
            if (res['cache_flag']) {
                alert('Response was loaded from cache.')
            }
            $('#text-to-translate').val($('#text-to-translate').val() + res['text'] + '\n');
            $('#translation-result').val($('#translation-result').val() + res['translation'] + '\n');
            playAudio();
            moveCursor();
        } else {
            console.log('Failed to translate from audio');
        }
    }
   
    var fd = new FormData();
    var filename = new Date().toISOString();
    fd.append("audio_data", blob, filename);
    xhr.open("POST","/translate-audio",true);
    xhr.send(fd);
}

function playAudio() {
    $.ajax({
        url: '/play-audio',
        type: 'GET',

        success: function( response ) {
                $('audio #source').attr('src', "data:audio/x-wav; " + response);
                $('audio').get(0).load();
                $('audio').get(0).play();
        }
    });
}

function moveCursor() {
    var translateVal = document.getElementById('text-to-translate');
    translateVal.focus();
    var position = translateVal.selectionEnd;
    if (translateVal.value != '') {
        position.value = translateVal.value.substring(0, position) + '\n' + translateVal.value.substring(position);
    }
    position.selectionEnd = position;
}

function translate() {
    var translateVal = $('#text-to-translate').val();
    var translateRequest = {'text': translateVal};

    if ((typeof rec !== 'undefined') && rec.recording) {
        rec.stop();
        gumStream.getAudioTracks()[0].stop();
        rec.exportWAV(getAudio);
    }

    else if (translateVal !== "") {
        $.ajax({
            url: '/translate-text',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            dataType: 'json',
            data: JSON.stringify(translateRequest),
            success: function (response) {
                var res = JSON.parse(JSON.stringify(response));
                if (res['cache_flag']) {
                    alert('Response was loaded from cache.');
                    $('#translation-result').val($('#translation-result').val() + res['translation'] + '\n');
                }
                else {
                    $('#translation-result').val(res['translation'] + '\n');
                }
                playAudio();
                moveCursor();
            }
        });
    }
}



$(function() {
    $("#translate").on("click", function(e) {
        e.preventDefault();
        translate();
    });

    $("#record").on("click", function(e) {
        e.preventDefault();
        var constraints = { audio: true, video: false };
        navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
            audioContext = new AudioContext();
            gumStream = stream;
            input = audioContext.createMediaStreamSource(stream);
            rec = new Recorder(input, {numChannels: 1});
            rec.record();
        });
    });

    $("#clear").on("click", function(e) {
        e.preventDefault();
        document.getElementById("text-to-translate").value = '';
        document.getElementById("translation-result").value = '';
        $.getJSON('/clear-history', {});
    });
});