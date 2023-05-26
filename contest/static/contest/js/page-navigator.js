class PageNavigator {
    constructor(options) {
        this.pageElement = this.getElement(options.pageElement);
        this.pageElementSelector = this.getElementSelector(options.pageElement);
        this.navElement = this.getElement(options.navElement);
        this.navElementSelector = this.getElementSelector(options.navElement);
        this.domParser = new DOMParser();
        this.navElement.addEventListener('click', this);
    }

    handleEvent(event) {
        let target = event.target;
        if (target.tagName !== 'A') {
            target = event.target.closest('a');
            if (!this.navElement.contains(target))
                return;
        }
        event.preventDefault();
        const url = target.getAttribute('href');
        fetch(url, {cache: "no-store"})
            .then(response => response.text())
            .then(data => {
                const newDocument = this.domParser.parseFromString(data, 'text/html');
                const newPageElement = newDocument.querySelector(this.pageElementSelector);
                const newNavElement = newDocument.querySelector(this.navElementSelector);
                this.pageElement.innerHTML = newPageElement.innerHTML;
                this.navElement.innerHTML = newNavElement.innerHTML;
                history.replaceState(null, document.title, url);
            })
            .catch(error => {
                console.log(error);
            });
    }

    getElement(option) {
        if (typeof option === 'string')
            return document.querySelector(option);
        return option;
    }

    getElementSelector(option) {
        if (typeof option === 'string')
            return option;
        return '#' + option.id;
    }
}
