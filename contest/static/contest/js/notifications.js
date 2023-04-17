function decrementUnreadCounterBadge() {
    let unread_notifications_count_element = document.getElementById('unread_notifications_count');
    if (!unread_notifications_count_element)
        return;
    let updated_count = parseInt(unread_notifications_count_element.innerText) - 1;
    if (updated_count > 0)
        unread_notifications_count_element.innerText = updated_count.toString();
    else
        unread_notifications_count_element.remove();
}

function markNotificationAsRead(notification_element) {
    if (notification_element.getAttribute('data-unread') !== "true")
        return;
    if (window.mark_notifications_as_read_url === undefined) {
        console.log("window.mark_notifications_as_read_url is not set!");
        return;
    }
    notification_element.setAttribute('data-unread', "false");
    let notification_id = JSON.parse(notification_element.getAttribute('data-id'));
    let form_data = new FormData();
    form_data.append('unread_notifications_ids', notification_id);
    let options = {
        method: 'POST',
        headers: {'ContentType': 'application/json', 'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        cache: 'no-store',
        body: form_data
    };
    fetch(window.mark_notifications_as_read_url, options)
        .then(response => {
            if (response.ok) {
                notification_element.classList.remove('bg-light');
                notification_element.onmouseover = null;
                decrementUnreadCounterBadge();
            } else {
                notification_element.setAttribute('data-unread', "true");
            }
        })
        .catch(error => {
            console.log(error);
            notification_element.setAttribute('data-unread', "true");
        });
}
