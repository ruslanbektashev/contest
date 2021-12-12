class TaskProgress {
    constructor(progress_url, execution_list_url, poll_interval, max_retries) {
        this.progress_bar_element = document.getElementById('progress-bar');
        this.progress_bar_message_element = document.getElementById('progress-bar-message');
        this.execution_list_element = document.getElementById('execution_list');
        this.btn_submission_evaluate_element = document.getElementById('btn_submission_evaluate');
        this.btn_submission_evaluate_text = this.btn_submission_evaluate_element.innerText;
        this.progress_url = progress_url;
        this.task_id = '';
        this.execution_list_url = execution_list_url;
        this.poll_interval = poll_interval;
        this.retry = 0;
        this.max_retries = max_retries;
        this.state = 'initial';
    }

    onProgress(json) {
        if (this.setState('progress')) {
            this.progress_bar_element.classList.add('bg-info');
        }
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
        if (this.setState('finished')) {
            this.progress_bar_element.classList.add('bg-' + json.class);
        }
        if (json.success) {
            this.progress_bar_message_element.textContent = json.result;
        } else {
            this.progress_bar_message_element.textContent = "Произошла ошибка в системе проверки";
        }
        this.task_id = '';
    }

    onError(error) {
        if (this.setState('finished')) {
            this.progress_bar_element.classList.add('bg-danger');
        }
        this.progress_bar_message_element.textContent = "Произошла ошибка при получении статуса";
        this.task_id = '';
    }

    setState(state) {
        if (this.state !== state) {
            this.state = state;
            this.progress_bar_element.classList.remove('bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary', 'bg-primary');
            if (state === 'progress') {
                this.btn_submission_evaluate_element.innerHTML = '<i class="fa fa-circle-o-notch fa-spin fa-fw"></i><span class="sr-only">Проверяется...</span>';
                this.btn_submission_evaluate_element.classList.add('disabled');
            } else {
                this.btn_submission_evaluate_element.innerHTML = this.btn_submission_evaluate_text;
                this.btn_submission_evaluate_element.classList.remove('disabled');
                this.progress_bar_element.style.width = '100%';
                this.progress_bar_message_element.style.color = 'white';
            }
            return true;
        }
        return false;
    }

    clearProgressBar() {
        this.progress_bar_element.style.width = '0%';
        this.progress_bar_message_element.style.color = 'black';
        this.progress_bar_message_element.textContent = "";
        this.execution_list_element.innerHTML = '';
    }

    updateProgress(json) {
        if (!json.complete) {
            this.onProgress(json);
        } else {
            this.onSuccess(json);
        }
        return json.complete;
    }

    retryPoll(error) {
        if (++this.retry < this.max_retries) {
            this.btn_submission_evaluate_element.innerHTML = '<i class="text-danger fa fa-circle-o-notch fa-spin fa-fw"></i><span class="sr-only">Loading...</span>';
            this.delayPoll(this.poll_interval + this.retry * 500);
        } else {
            this.onError(error);
        }
    }

    delayPoll(timeout) {
        setTimeout(this.poll.bind(this), timeout);
    }

    async poll() {
        let response = await fetch(this.progress_url + this.task_id, {cache: "no-store"});
        if (response.ok) {
            let progress = await response.json();
            if (!this.updateProgress(progress)) {
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

    startPolling(task_id) {
        this.task_id = task_id;
        this.clearProgressBar();
        return this.poll();
    }
}
