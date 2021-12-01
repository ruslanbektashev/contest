class ReadWatcher {
    constructor(marker_url) {
        this.mark_notifications_as_read_url = marker_url;
        this.notifications = document.getElementById('notifications');
        this.unread_notifications_ids = [];
        this.options = { method: 'POST', headers: { 'ContentType': 'application/json' }, cache: 'no-store' }
    }

    updateUnreadCounterBadge() {
        let unread_notifications_count_element = document.getElementById('unread_notifications_count');
        let updated_count = parseInt(unread_notifications_count_element.innerText) - this.unread_notifications_ids.length;
        if (updated_count > 0)
            unread_notifications_count_element.innerText = updated_count.toString();
        else
            unread_notifications_count_element.remove();
    }

    markNotificationsAsRead() {
        if (this.unread_notifications_ids.length > 0) {
            this.options['body'] = JSON.stringify({ unread_notifications_ids: this.unread_notifications_ids });
            this.updateUnreadCounterBadge();
            this.unread_notifications_ids = [];
            fetch(this.mark_notifications_as_read_url, this.options).then(response => {});
        }
        setTimeout(this.marknotificationsAsRead.bind(this), 1000);
    }

    isInViewPoint(element) {
        let bounding = element.getBoundingClientRect();
        return (bounding.top >= 0 && bounding.left >= 0 &&
                bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                bounding.right <= (window.innerWidth || document.documentElement.clientWidth));
    }

    handleEvent(event) {
        for(let notification of this.notifications.children) {
            let is_unread = JSON.parse(notification.getAttribute('data-unread'));
            if (is_unread) {
                let notification_id = parseInt(notification.getAttribute('data-id'));
                let notification_body = notification.getElementsByClassName('notification-body')[0];
                if (this.isInViewPoint(notification_body) && !this.unread_notifications_ids.includes(notification_id)) {
                    notification.classList.remove('bg-light');
                    notification.removeAttribute('data-unread');
                    this.unread_notifications_ids.push(notification_id);
                }
            }
        }
    }
}
