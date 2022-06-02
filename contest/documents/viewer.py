from re import sub
from csv import reader
from io import BytesIO, StringIO
from tempfile import TemporaryFile

try:
    from aspose import slides as aspose_slides
except ImportError:
    aspose_slides = None
try:
    from aspose import words as aspose_words
except ImportError:
    aspose_words = None
from mammoth import convert_to_html
from openpyxl import Workbook, load_workbook
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import CppLexer
from xls2xlsx import XLS2XLSX
from xlsx2html import xlsx2html

from django.http import Http404
from contest.documents import replaces


def remove_ppt_watermarks(content):
    content = sub(replaces.PPT_WM_1, replaces.TSPAN, content)
    content = sub(replaces.PPT_WM_2, replaces.BLANK, content)
    content = sub(replaces.PPT_WM_3, replaces.BLANK, content)
    content = sub(replaces.PPT_ST_1_BEFORE, replaces.PPT_ST_1_AFTER, content)
    content = sub(replaces.PPT_ST_2_BEFORE, replaces.PPT_ST_2_AFTER, content)
    content = sub(replaces.PPT_ST_3_BEFORE, replaces.PPT_ST_3_AFTER, content)
    return content


def to_html(attachment):
    result = 'Неизвестный тип файла. Загрузите его и воспользуйтесь локальным средством просмотра.', 0
    attachment_ext = attachment.extension()
    if attachment_ext in ('.h', '.hpp', '.c', '.cpp'):
        try:
            content = attachment.file.read()
        except FileNotFoundError:
            raise Http404("File %s does not exist." % attachment.filename)
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        result = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter), 0
    elif attachment_ext in ('.ppt', '.pptx'):
        if aspose_slides is not None:
            ppt_file = aspose_slides.Presentation(attachment.file.path)
            options = aspose_slides.export.HtmlOptions()
            byte_stream = BytesIO()
            ppt_file.save(byte_stream, aspose_slides.export.SaveFormat.HTML, options)
            html_content = str(byte_stream.getvalue(), 'utf-8')
            html_content = remove_ppt_watermarks(html_content)
            result = html_content, 1
        else:
            result = ('Невозможно отобразить файл. Пакет Aspose.Slides не найден.\n' +
                      'Загрузите файл и воспользуйтесь локальным средством просмотра.'), 0
    elif attachment_ext in ('.xls', '.xlsx'):
        if attachment_ext == '.xls':
            temp = TemporaryFile()
            converter = XLS2XLSX(attachment.file.path)
            converter.to_xlsx(temp)
        else:
            temp = attachment.file.path
        html_sheets = dict()
        workbook = load_workbook(temp)
        for i in range(len(workbook.sheetnames)):
            xlsx_file = temp
            current_sheet = StringIO()
            xlsx2html(xlsx_file, current_sheet, locale='en', sheet=i)
            current_sheet.seek(0)
            current_sheet_html = current_sheet.read()
            html_sheets[workbook.sheetnames[i]] = current_sheet_html
        sheets = ''.join(f'<hr><h3 id="fsheet{id(sheet_name)}">{sheet_name}</h3><hr>{value}'
                         for sheet_name, value in html_sheets.items())
        nav = '<br><ul>{}</ul>'.format(''.join(f'<li><a href="#fsheet{id(sheet_name)}">{sheet_name}</a></li>'
                                               for sheet_name in html_sheets.keys()))
        result = (sheets + nav), 0
    elif attachment_ext == '.csv':
        temp = TemporaryFile()
        workbook = Workbook()
        worksheet = workbook.active
        with open(attachment.file.path, 'r') as file:
            for row in reader(file):
                worksheet.append(row)
        workbook.save(temp)
        sheet = StringIO()
        xlsx2html(temp, sheet, locale='en')
        sheet.seek(0)
        html_content = sheet.read()
        result = html_content, 0
    elif attachment_ext == '.doc':
        if aspose_words is not None:
            doc_file = aspose_words.Document(attachment.file.path)
            byte_stream = BytesIO()
            doc_file.save(byte_stream, aspose_words.SaveFormat.DOCX)
            html_content = convert_to_html(byte_stream).value
            result = sub(replaces.DOC_WM_1, replaces.BLANK, html_content), 0
        else:
            result = ('Невозможно отобразить файл. Пакет Aspose.Words не найден.\n' +
                      'Загрузите файл и воспользуйтесь локальным средством просмотра.'), 0
    elif attachment_ext == '.docx':
        result = convert_to_html(attachment.file.path).value, 0
    return result
