class NotificationsReadWatcher {
    constructor() {
        this.unread_notifications = [];
    }

    handleEvent(event) {
        if (event.target.getAttribute('data-unread') !== "true")
            return;
        event.target.setAttribute('data-unread', "false");
        this.unread_notifications.push(event.target);
    }
}

function updateUnreadNotificationsCounterBadge(read_notifications_count) {
    let unread_notifications_count_element = document.getElementById('unread_notifications_count');
    if (!unread_notifications_count_element)
        return;
    let updated_count = parseInt(unread_notifications_count_element.innerText) - read_notifications_count;
    if (updated_count > 0)
        unread_notifications_count_element.innerText = updated_count.toString();
    else
        unread_notifications_count_element.remove();
}

function markNotificationsAsRead(notifications_mark_as_read_url, unread_notification_elements) {
    if (unread_notification_elements.length === 0)
        return;
    let data = {
        unread_notifications_ids: unread_notification_elements.map(el => JSON.parse(el.getAttribute('data-id')))
    }
    let options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        cache: 'no-store',
        body: JSON.stringify(data)
    };
    fetch(notifications_mark_as_read_url, options)
        .then(response => {
            if (response.ok) {
                unread_notification_elements.forEach((value, i, a) => {
                    value.classList.remove('bg-light');
                    value.onmouseover = null;
                });
                updateUnreadNotificationsCounterBadge(unread_notification_elements.length);
            } else {
                unread_notification_elements.forEach((value, i, a) => value.setAttribute('data-unread', "true"));
            }
        })
        .catch(error => {
            console.log(error);
            unread_notification_elements.forEach((value, i, a) => value.setAttribute('data-unread', "true"));
        });
}
