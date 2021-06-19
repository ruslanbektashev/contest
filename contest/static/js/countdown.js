function countdownText(x, t, d = " ")
{
    let text = d;
    if (x > 4 && x < 21)
        text = t[0];
    else if((x > 1 && x < 5) || (x % 10 > 1 && x % 10 < 5))
        text = t[1];
    else if (x === 1 || x % 10 === 1)
        text = t[2];
    else if ((x % 10 > 4 && x % 10 <= 9) || x % 10 === 0)
        text = t[3];
    return text;
}

function startCountdown(datetime) {
    let countdown_wrapper_element = document.getElementById("countdown_wrapper");
    let countdown_to_deadline_element = document.getElementById("countdown_to_deadline");
    if (datetime === "") {
        countdown_wrapper_element.innerHTML = "";
        return;
    }

    let deadline = new Date(datetime).getTime();

    let x = setInterval(function () {
        let now = new Date().getTime();

        let distance = deadline - now;

        let days = Math.floor(distance / (1000 * 60 * 60 * 24));
        let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        let countdown_to_deadline = "";
        let t_days = " д. ";
        let t_hours = " ч. ";
        let t_minutes = " м. ";
        let t_seconds = " с. ";

        t_days = countdownText(days, [" дней ", " дня ", " день ", " дней "], " д. ");
        t_hours = countdownText(hours, [" часов ", " часа ", " час ", " часов "], " ч. ");
        t_minutes = countdownText(minutes, [" минут ", " минуты ", " минута ", " минут "], " м. ");
        t_seconds = countdownText(seconds, [" секунд ", " секунды ", " секунда ", " секунд "], " с. ");

        if (days !== 0)
            countdown_to_deadline += days + t_days;
        if (hours !== 0)
            countdown_to_deadline += hours + t_hours;
        if (minutes !== 0)
            countdown_to_deadline += minutes + t_minutes;
        /*if (seconds !== 0)
            countdown_to_deadline += seconds + t_seconds;*/
        countdown_to_deadline = countdown_to_deadline.trim();

        try {
            countdown_to_deadline_element.innerText = countdown_to_deadline;

            if (distance < 0) {
                clearInterval(x);
                countdown_wrapper_element.innerHTML = "";
            }
        } catch {
            clearInterval(x);
        }
    }, 1000);
}
