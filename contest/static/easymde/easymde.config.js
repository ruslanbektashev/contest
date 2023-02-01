let easymdeConfig = {
    'default': {
        autofocus: true,
        lineNumbers: true,
        spellChecker: false,
        sideBySideFullscreen: false,
        status: false,
        toolbar: [
            {
                name: 'bold',
                action: EasyMDE.toggleBold,
                className: "fa fa-bold",
                title: "Полужирный"
            },
            {
                name: 'italic',
                action: EasyMDE.toggleItalic,
                className: "fa fa-italic",
                title: "Курсив"
            },
            {
                name: 'strikethrough',
                action: EasyMDE.toggleStrikethrough,
                className: "fa fa-strikethrough",
                title: "Зачёркнутый"
            },
            "|",
            {
                name: 'heading',
                action: EasyMDE.toggleHeadingSmaller,
                className: "fa fa-header",
                title: "Заголовок"
            },
            {
                name: 'quote',
                action: EasyMDE.toggleBlockquote,
                className: "fa fa-quote-left",
                title: "Цитата"
            },
            {
                name: 'unordered-list',
                action: EasyMDE.toggleUnorderedList,
                className: "fa fa-list-ul",
                title: "Список"
            },
            {
                name: 'ordered-list',
                action: EasyMDE.toggleOrderedList,
                className: "fa fa-list-ol",
                title: "Нумерованный список"
            },
            {
                name: 'code',
                action: EasyMDE.toggleCodeBlock,
                className: "fa fa-code",
                title: "Код"
            },
            "|",
            {
                name: 'table_', // conflicts with table class from bootstrap
                action: EasyMDE.drawTable,
                className: "fa fa-table",
                title: "Таблица"
            },
            {
                name: 'link',
                action: EasyMDE.drawLink,
                className: "fa fa-link",
                title: "Ссылка"
            },
            {
                name: 'image',
                action: EasyMDE.drawImage,
                className: "fa fa-picture-o",
                title: "Изображение"
            },
            {
                name: 'horizontal-rule',
                action: EasyMDE.drawHorizontalRule,
                className: "fa fa-minus",
                title: "Горизонтальная линия"
            },
            "|",
            {
                name: 'undo',
                action: EasyMDE.undo,
                className: "fa fa-undo",
                title: "Отмена"
            },
            {
                name: 'redo',
                action: EasyMDE.redo,
                className: "fa fa-repeat",
                title: "Возврат"
            },
            "|",
            {
                name: 'side-by-side',
                action: EasyMDE.toggleSideBySide,
                className: "fa fa-columns no-disable no-mobile",
                title: "Предпросмотр справа"
            },
            {
                name: 'preview',
                action: EasyMDE.togglePreview,
                className: "fa fa-eye no-disable",
                title: "Предпросмотр"
            },
            "|",
            {
                name: 'guide',
                action: "https://www.markdownguide.org/basic-syntax/",
                className: "fa fa-question-circle",
                title: "Помощь по Markdown"
            },
        ]
    }
}
