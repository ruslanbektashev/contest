let ckeditorConfigs = {
    'default': {
        language: 'ru',
        ui: {
            viewportOffset: { top: 63, right: 0, bottom: 0, left: 0 } // or set dynamically: editor.ui.viewportOffset
        },
        removePlugins: [
            //'Code',
            //'CodeBlock',
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
			'code', 'codeBlock', '|',
			// 'insertImage', 'uploadImage', '|',
			'undo', 'redo', // '|',
			// 'sourceEditing'
        ]
    },
	'markdown': {
        language: 'ru',
        ui: {
            viewportOffset: { top: 63, right: 0, bottom: 0, left: 0 } // or set dynamically: editor.ui.viewportOffset
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

function initCKEditor(element, config) {
    const contestNavBar = document.getElementById('contestNavBar');
    if (contestNavBar)
        ckeditorConfigs[config]['ui']['viewportOffset']['top'] = contestNavBar.offsetHeight;
    ClassicEditor.create(element, ckeditorConfigs[config])
        .then(editor => {
            window.editor = editor;
            //console.log(Array.from(editor.ui.componentFactory.names()));
        })
        .catch(error => {
            console.log(error);
        });
}

function dropCKEditor() {
    window.editor.destroy()
        .catch(error => {
            console.log(error);
        });
}

window.CKEDITOR_TRANSLATIONS = window.CKEDITOR_TRANSLATIONS || {};
window.CKEDITOR_TRANSLATIONS['ru'] = window.CKEDITOR_TRANSLATIONS['ru'] || {};
window.CKEDITOR_TRANSLATIONS['ru'].dictionary =  window.CKEDITOR_TRANSLATIONS['ru'].dictionary || {};
Object.assign(window.CKEDITOR_TRANSLATIONS['ru'].dictionary, {
    "Source": "Исходник"
});
