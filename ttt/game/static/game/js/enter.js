(function ($) {
    $(function () {
        let latency = $("#enter").data("latency"),
            play = $("#play");

        play.on("click", function () {
            $.ajax({
                type: 'GET',
                url: play.data('url'),
                beforeSend: function () {
                    $("#enter").html("Please Wait for the second Player");
                },
                success: responseData => {
                    console.log("Answer is: " + JSON.stringify(responseData));
                    let redirectTo = responseData.room_id + '/';
                    if (responseData.wait) {
                        setTimeout(
                            function () {
                                window.location.href = redirectTo;
                            },
                            latency * 1000
                        );
                    } else {
                        window.location.href = redirectTo;
                    }
                },
                error: responseData => console.log("Cannot get room id " + responseData)
            });
        });
    });
}(jQuery));

