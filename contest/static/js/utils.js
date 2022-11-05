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

function toggleOpacity(firstElement, secondElement, firstTime, secondTime) {
    firstElement.style.transition = 'opacity ' + firstTime;
    firstElement.style.opacity = '0';
    const hider = () => {
        firstElement.hidden = true;
        firstElement.removeEventListener('transitionend', hider);
    };
    const shower = () => {
        secondElement.hidden = false;
        const refresh = secondElement.offsetHeight;
        secondElement.style.transition = 'opacity ' + secondTime;
        secondElement.style.opacity = '1';
        firstElement.removeEventListener('transitionend', shower);
    }
    firstElement.addEventListener('transitionend', hider)
    firstElement.addEventListener('transitionend', shower)
}

function adjustStickyColumns(table_element, columns_num) {
    for (let i = 0; i < table_element.rows.length; i++) {
        let offsetSum = 0;
        for (let j = 1; j < columns_num; j++) {
            offsetSum += table_element.rows[i].cells[j - 1].offsetWidth;
            table_element.rows[i].cells[j].style.left = (offsetSum - 1) + "px";
        }
    }
}
