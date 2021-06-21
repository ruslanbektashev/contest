function toggleText(elem, firstText, secondText) {
    if (elem.innerText === firstText) {
        elem.innerText = secondText;
    } else {
        elem.innerText = firstText;
    }
}

function toggleHTML(elem, firstHTML, secondHTML) {
    if (elem.innerHTML === firstHTML) {
        elem.innerHTML = secondHTML;
    } else {
        elem.innerHTML = firstHTML;
    }
}
