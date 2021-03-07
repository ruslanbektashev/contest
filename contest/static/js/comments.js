class ReadWatcher {
    constructor(marker_url) {
        this.mark_comments_as_read_url = marker_url;
        this.comments = document.getElementById('comments');
        this.unread_comments_ids = [];
        this.options = { method: 'POST', headers: { 'ContentType': 'application/json' }, cache: 'no-store' }
    }

    updateUnreadCounterBadge() {
        let unread_comments_count_element = document.getElementById('unread_comments_count');
        let updated_count = parseInt(unread_comments_count_element.innerText) - this.unread_comments_ids.length;
        if (updated_count > 0)
            unread_comments_count_element.innerText = updated_count.toString();
        else
            unread_comments_count_element.remove();
    }

    markCommentsAsRead() {
        if (this.unread_comments_ids.length > 0) {
            this.options['body'] = JSON.stringify({ unread_comments_ids: this.unread_comments_ids });
            this.updateUnreadCounterBadge();
            this.unread_comments_ids = [];
            fetch(this.mark_comments_as_read_url, this.options).then(response => {});
        }
        setTimeout(this.markCommentsAsRead.bind(this), 1000);
    }

    isInViewPoint(element) {
        let bounding = element.getBoundingClientRect();
        return (bounding.top >= 0 && bounding.left >= 0 &&
                bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                bounding.right <= (window.innerWidth || document.documentElement.clientWidth));
    }

    handleEvent(event) {
        for(let comment of this.comments.children) {
            let is_unread = JSON.parse(comment.getAttribute('data-unread'));
            if (is_unread) {
                let comment_id = parseInt(comment.getAttribute('data-id'));
                let comment_footer = comment.getElementsByClassName('comment-footer')[0];
                if (this.isInViewPoint(comment_footer) && !this.unread_comments_ids.includes(comment_id)) {
                    comment.classList.remove('bg-light');
                    comment.removeAttribute('data-unread');
                    this.unread_comments_ids.push(comment_id);
                }
            }
        }
    }
}
