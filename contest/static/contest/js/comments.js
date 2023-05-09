class CommentsReadWatcher {
    constructor(comments_container_element) {
        this.comments_container_element = comments_container_element;
        this.unread_comment_elements = [];
    }

    isInViewPoint(element) {
        let bounding = element.getBoundingClientRect();
        return (bounding.top >= 0 && bounding.left >= 0 &&
                bounding.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                bounding.right <= (window.innerWidth || document.documentElement.clientWidth));
    }

    handleEvent(event) {
        for (let comment of this.comments_container_element.children) {
            if (comment.getAttribute('data-unread') === "true") {
                let comment_footer = comment.getElementsByClassName('contest-comment-footer')[0];
                if (this.isInViewPoint(comment_footer)) {
                    comment.setAttribute('data-unread', "false");
                    this.unread_comment_elements.push(comment);
                }
            }
        }
    }
}

function updateUnreadCommentsCounterBadge(read_comments_count) {
    let unread_comments_count_element = document.getElementById('unread_comments_count');
    if (!unread_comments_count_element)
        return;
    let updated_count = parseInt(unread_comments_count_element.innerText) - read_comments_count;
    if (updated_count > 0)
        unread_comments_count_element.innerText = updated_count.toString();
    else
        unread_comments_count_element.remove();
}

function markCommentsAsRead(comments_mark_as_read_url, unread_comment_elements) {
    if (unread_comment_elements.length === 0)
        return;
    let data = {
        unread_comments_ids: unread_comment_elements.map(el => JSON.parse(el.getAttribute('data-id')))
    }
    let options = {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrftoken},
        mode: 'same-origin',
        cache: 'no-store',
        body: JSON.stringify(data)
    }
    fetch(comments_mark_as_read_url, options)
        .then(response => {
            if (response.ok) {
                unread_comment_elements.forEach((value, i, a) => {
                    value.classList.remove('bg-light');
                    value.onmouseover = null;
                });
                updateUnreadCommentsCounterBadge(unread_comment_elements.length);
            } else {
                unread_comment_elements.forEach((value, i, a) => value.setAttribute('data-unread', "true"));
            }
        })
        .catch(error => {
            console.log(error);
            unread_comment_elements.forEach((value, i, a) => value.setAttribute('data-unread', "true"));
        });
}
