class TaskProgress {
    constructor(progress_url, execution_list_url) {
        this.progress_bar_element = document.getElementById('progress-bar');
        this.progress_bar_message_element = document.getElementById('progress-bar-message');
        this.execution_list_element = document.getElementById('execution_list');
        this.execution_list_element.innerHTML = '';
        this.progress_url = progress_url;
        this.execution_list_url = execution_list_url;
        this.poll_interval = 1000;
        this.retry = 0;
        this.max_retries = 5;
    }

    onProgress(json) {
        this.progress_bar_element.classList.remove('bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary', 'bg-primary');
        this.progress_bar_element.classList.add('bg-info');
        if (json.progress > 0) {
            this.progress_bar_element.style.width = json.progress + '%';
            if (json.progress <= 50 && this.progress_bar_message_element.style.color === 'white') {
                this.progress_bar_message_element.style.color = 'black';
            } else if (json.progress > 50 && this.progress_bar_message_element.style.color === 'black') {
                this.progress_bar_message_element.style.color = 'white';
            }
            if (json.state === 'PENDING') {
                this.progress_bar_message_element.textContent = "Ждем своей очереди";
            } else if (json.state === 'STARTED') {
                this.progress_bar_message_element.textContent = "Компилируем";
            } else {
                this.progress_bar_message_element.textContent = json.state;
            }
        }
    }

    onSuccess(json) {
        this.progress_bar_element.classList.remove('bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary', 'bg-primary');
        this.progress_bar_element.classList.add('bg-' + json.class);
        this.progress_bar_element.style.width = '100%';
        this.progress_bar_message_element.style.color = 'white';
        if (json.success) {
            this.progress_bar_message_element.textContent = json.result;
        } else {
            this.progress_bar_message_element.textContent = "Произошла ошибка в системе проверки";
        }
    }

    onError(error) {
        this.progress_bar_element.classList.remove('bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary', 'bg-primary');
        this.progress_bar_element.classList.add('bg-danger');
        this.progress_bar_element.style.width = '100%';
        this.progress_bar_message_element.style.color = 'white';
        this.progress_bar_message_element.textContent = "Произошла ошибка при получении статуса";
    }

    updateBar(json) {
        if (!json.complete) {
            this.onProgress(json);
        } else {
            this.onSuccess(json);
        }
        return json.complete;
    }

    retryPoll(error) {
        if (++this.retry < this.max_retries) {
            this.delayPoll(this.poll_interval + this.retry * 500);
        } else {
            this.onError(error);
        }
    }

    delayPoll(timeout) {
        setTimeout(this.poll.bind(this), timeout);
    }

    async poll() {
        let response = await fetch(this.progress_url, {cache: "no-store"});
        if (response.ok) {
            let progress = await response.json();
            if (!this.updateBar(progress)) {
                this.delayPoll(this.poll_interval);
            } else {
                response = await fetch(this.execution_list_url, {cache: "no-store"});
                if (response.ok) {
                    this.execution_list_element.innerHTML = await response.text();
                } else {
                    let err = Error('fetch(executions): http status ' + response.status);
                    console.log(err);
                    this.retryPoll(err);
                }
            }
        } else {
            let err = Error('fetch(progress): http status ' + response.status);
            console.log(err);
            this.retryPoll(err);
        }
    }
}
