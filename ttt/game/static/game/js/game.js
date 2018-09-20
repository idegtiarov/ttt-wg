(function ($) {
    $(function() {
        let roomName = $('#desk_id').data('desk-name'),
            deskSocket = new WebSocket('ws://' + window.location.host + '/ws/desk/' + roomName + '/'),
            turn = false,
            latency = $("#desk_id").data("latency"),
            me = $("#me"),
            notme = $("#notme"),
            enemy = undefined,
            loop = 0,
            shake = 0;

        function setChoice(element) {
            if (!element.hasClass('avoid-click')) {
                let pointer = (turn) ? "0": "x";
                element.html(pointer);
                element.addClass("avoid-click");
                turn = !turn;
            }
        }

        function fulfillNumbers(playerWin, playerLost) {
            console.log(playerWin);
            let winPlayer = $("#{} > p > .wins".replace('{}', playerWin)),
                lostPlayer = $("#{} > p > .losts".replace('{}', playerLost)),
                wins  = Number(winPlayer.text()),
                losts = Number(lostPlayer.text());
            winPlayer.text(wins + 1);
            lostPlayer.text(losts + 1);
        }

        function setGameResult(key) {
            key ? fulfillNumbers("player", "enemy") : fulfillNumbers("enemy", "player");
        }

        function addGameResult(result){
            console.log('result is: ' + result);
            let key = result["win"];
            if (key === 'draw') {
                $("span.draws").each(function(){
                    let draws = Number($(this).text());
                    $(this).text(draws + 1);
                })
            } else {
                setGameResult(enemy ? (result["player"] === me.text() ? key : !key) : key);
            }


        }

        deskSocket.onmessage = function(e) {
            let data = JSON.parse(e.data),
                id = data['id'];
            console.log(data['result']);
            if (data.new_game) {
                $("#new_game").attr('hidden', true);
                $("span.item").each(function () {
                    $(this).removeClass('avoid-click');
                    $(this).removeClass('win');
                    $(this).html('');
                })
            } else if (data.user) {
                if (data.user != me.text()) {
                    console.log("My Enemy is " + data.user)
                    notme.text(data.user);
                    notme.addClass('chosen');
                    if ( !shake ) {
                        deskSocket.send(JSON.stringify({
                            "user": me.text(),
                        }));
                    }
                    shake = true;
                    enemy = true;
                    $("#desk_id").removeClass('pause');
                } else {
                    if (shake && !notme.hasClass('chosen')) {
                        console.log("AI is my enemy");
                        notme.text("AI");
                        $("#desk_id").removeClass('pause');
                        enemy = false;
                    } else if (loop === 0) {
                        loop += 1;
                        shake = true;
                        setTimeout(function () {
                            console.log("Trying to do handshake")
                            deskSocket.send(JSON.stringify({
                                "user": me.text(),
                            }));
                        }, latency * 1000)
                    }
                }

            } else {
                setChoice($('#' + id));
                console.log("result is " + data.result)
                if (data['result']) {
                    console.log('result is' + data['result']['win'])
                    addGameResult(data['result']);
                    $("span.item").each(function () {
                        $(this).addClass('avoid-click')
                    });
                    console.log(data['result']);
                    $.each(data['result']['ids'], function (index, val) {
                        $('#' + val).addClass('win');
                    });
                    $("#new_game").attr('hidden', false);
                }
                data.username != me.text() ? $("#desk_id").removeClass('pause'):true;
            }
        };

        deskSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        $("#new_game").on("click", function () {
            deskSocket.send(JSON.stringify({
                "new_game": true,
            }));
        });

        $('span.item').on("click", function () {
            $("#desk_id").addClass('pause');
            setChoice($(this));
            deskSocket.send(JSON.stringify({
                "enemy": enemy,
                "char": $(this).text(),
                "id": $(this).attr("id"),
            }))

        });

        // Handshake msg

        $(function () {
            $("#desk_id").addClass('pause');
            console.log('Shake is sent');
            deskSocket.send(JSON.stringify({
                "user": me.text(),
                "loop": loop,
            }));
        });

    });
}(jQuery));
