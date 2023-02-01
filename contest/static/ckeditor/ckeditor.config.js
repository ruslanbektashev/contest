let ckeditorConfigs = {
    'default': {
        language: 'ru',
        ui: {
            viewportOffset: { top: 57, right: 0, bottom: 0, left: 0 } // or set dynamically: editor.ui.viewportOffset
        },
        removePlugins: [
            'Code',
            'CodeBlock',
            'DataFilter',
            'DataSchema',
            'GeneralHtmlSupport',
            'ImageInsert',
            'ImageUpload',
            'Markdown',
            'SimpleUploadAdapter',
            'SourceEditing',
        ],
        toolbar: [
            'heading', '|',
			'bold', 'italic', 'underline', 'strikethrough', 'blockQuote', 'bulletedList', 'numberedList', '|',
			'outdent', 'indent', 'alignment', '|',
			'fontFamily', 'fontSize', 'fontColor', '|',
			'link', 'insertTable', '|',
			'undo', 'redo', // '|',
			// 'sourceEditing'
        ]
    },
	'markdown': {
        language: 'ru',
        ui: {
            viewportOffset: { top: 57, right: 0, bottom: 0, left: 0 } // or set dynamically: editor.ui.viewportOffset
        },
        removePlugins: [
            'DataFilter',
            'DataSchema',
            'FontColor',
            'FontFamily',
            'FontSize',
            'GeneralHtmlSupport',
            'ImageInsert',
            'ImageUpload',
            'SimpleUploadAdapter',
        ],
        toolbar: [
            'heading', '|',
			'bold', 'italic', 'blockQuote', 'bulletedList', 'numberedList', 'horizontalLine', '|',
			'code', 'codeBlock', '|',
			'link', 'insertTable', '|',
			'undo', 'redo', '|',
			'sourceEditing'
        ],
		codeBlock: {
			languages: [
				{ language: 'plaintext', label: 'Простой текст' }
			]
		}
    }
}
