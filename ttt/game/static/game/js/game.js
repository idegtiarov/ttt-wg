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

        // Set player's choice
        function setChoice(element) {
            if (!element.hasClass('avoid-click')) {
                let pointer = (turn) ? "0": "x";
                element.html(pointer);
                element.addClass("avoid-click");
                turn = !turn;
            }
        }

        // Update current player's statistics
        function fulfillNumbers(playerWin, playerLost) {
            console.log("Win " + playerWin);
            let winPlayer = $("#{} > p > .wins".replace('{}', playerWin)),
                lostPlayer = $("#{} > p > .losts".replace('{}', playerLost)),
                wins  = Number(winPlayer.text()),
                losts = Number(lostPlayer.text());
            winPlayer.text(wins + 1);
            lostPlayer.text(losts + 1);
        }

        // Update Game result for both players
        function setGameResult(key) {
            if (key) {
                fulfillNumbers("player", "enemy");
                updateStats(1, 0, 0)
            } else {
                fulfillNumbers("enemy", "player");
                updateStats(0, 1, 0)
            }
        }

        // Handel the result of the recent game.
        function addGameResult(result){
            console.log(result);
            let key = result["win"];
            if (key === 'draw') {
                $("span.draws").each(function(){
                    let draws = Number($(this).text());
                    $(this).text(draws + 1);
                });
                updateStats(0, 0, 1)
            } else {
                setGameResult(enemy ? (result["player"] === me.text() ? key : !key) : key);
            }


        }

        // Handle websocket messages
        deskSocket.onmessage = function(e) {
            let data = JSON.parse(e.data),
                id = data['id'];
            console.log(data['result']);
            if (data.new_game) {
                // Handle new game start request
                $("#new_game").attr('hidden', true);
                $("span.item").each(function () {
                    $(this).removeClass('avoid-click');
                    $(this).removeClass('win');
                    $(this).html('');
                })
            } else if (data.user) {
                // Handle handshake
                if (data.user != me.text()) {
                    console.log("My Enemy is " + data.user);
                    notme.text(data.user);
                    notme.addClass('chosen');
                    if ( !shake || data.primary) {
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
                // Handle main game process
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
                data.username != me.text() || !enemy ? $("#desk_id").removeClass('pause'):true;
            }
        };

        deskSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly!');
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

        // Update player's stats function.
        function updateStats(win, lost, draw) {
            $.ajax({
                type: 'POST',
                url: $("#stats").data('url'),
                data: {
                    'progress': JSON.stringify({
                        'enemy': enemy,
                        'wins': {
                            'win': win, 'lost': lost, 'draw': draw
                        },
                    }),
                },
                success: responseData => {
                    $("#ai-stats").text(responseData['ai']);
                    $("#enemy-stats").text(responseData['enemy']);
                },
                error: responseData => console.log("Cannot update user's progress. " + responseData)
            });
        };

        // Handshake msg on page load/reload

        $("#desk_id").addClass('pause');

        updateStats(0, 0, 0);

        if (!deskSocket.readyState){
            setTimeout(function () {
                deskSocket.send(JSON.stringify({
                    "user": me.text(),
                    "loop": loop,
                    "primary": true,
                }));
            }, 1000
            );
        } else {
            deskSocket.send(JSON.stringify({
                "user": me.text(),
                "loop": loop,
                "primary": true,
            }));
        }
    });
}(jQuery));
