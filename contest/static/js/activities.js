class ReadWatcher {
    constructor(marker_url) {
        this.mark_activities_as_read_url = marker_url;
        this.activities = document.getElementById('activities');
        this.unread_activities_ids = [];
        this.options = { method: 'POST', headers: { 'ContentType': 'application/json' }, cache: 'no-store' }
    }

    updateUnreadCounterBadge() {
        let unread_activities_count_element = document.getElementById('unread_activities_count');
        let updated_count = parseInt(unread_activities_count_element.innerText) - this.unread_activities_ids.length;
        if (updated_count > 0)
            unread_activities_count_element.innerText = updated_count.toString();
        else
            unread_activities_count_element.remove();
    }

    markActivitiesAsRead() {
        if (this.unread_activities_ids.length > 0) {
            this.options['body'] = JSON.stringify({ unread_activities_ids: this.unread_activities_ids });
            this.unread_activities_ids = [];
            fetch(this.mark_activities_as_read_url, this.options).then(response => {});
        }
        setTimeout(this.markActivitiesAsRead.bind(this), 1000);
    }

    isInViewPoint(element) {
        let bounding = element.getBoundingClientRect();
        return (bounding.top >= 0 && bounding.left >= 0 &&
                bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                bounding.right <= (window.innerWidth || document.documentElement.clientWidth));
    }

    handleEvent(event) {
        for(let activity of this.activities.children) {
            let is_unread = JSON.parse(activity.getAttribute('data-unread'));
            if (is_unread) {
                let activity_id = parseInt(activity.getAttribute('data-id'));
                let activity_body = activity.getElementsByClassName('activity-body')[0];
                if (this.isInViewPoint(activity_body) && !this.unread_activities_ids.includes(activity_id)) {
                    activity.classList.remove('bg-light');
                    activity.removeAttribute('data-unread');
                    this.unread_activities_ids.push(activity_id);
                }
            }
        }
    }
}
