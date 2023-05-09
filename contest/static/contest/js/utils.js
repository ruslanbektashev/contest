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

function adjustStickyColumns(table_element) {
    for (let row of table_element.rows) {
        let offsetSum = 0;
        for (let cell of row.cells) {
            if (cell.cellIndex === 0)
                continue;
            if (!cell.classList.contains('contest-sticky-column'))
                break;
            offsetSum += cell.previousElementSibling.offsetWidth;
            cell.style.left = offsetSum + "px";
        }
    }
}
