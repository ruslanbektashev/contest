import re
import random

from csv import reader
from io import BytesIO, StringIO
from re import sub
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

from contest.documents import replaces
from contests.models import (Contest, Course, Problem)


def remove_ppt_watermarks(content):
    content = sub(replaces.PPT_WM_1, replaces.TSPAN, content)
    content = sub(replaces.PPT_WM_2, replaces.BLANK, content)
    content = sub(replaces.PPT_WM_3, replaces.BLANK, content)
    content = content.replace(replaces.PPT_ST_1_BEFORE, replaces.PPT_ST_1_AFTER)
    content = content.replace(replaces.PPT_ST_2_BEFORE, replaces.PPT_ST_2_AFTER)
    content = content.replace(replaces.PPT_ST_3_BEFORE, replaces.PPT_ST_3_AFTER)
    return content


def remove_doc_watermarks(content):
    return sub(replaces.DOC_WM_1, replaces.BLANK, content)


def to_html(attachment):
    result = None, False
    attachment_ext = attachment.extension()
    if attachment_ext in ('.h', '.hpp', '.c', '.cpp'):
        content = attachment.file.read()
        formatter = HtmlFormatter(linenos='inline', wrapcode=True)
        result = highlight(content.decode(errors='replace').replace('\t', ' ' * 4), CppLexer(), formatter), False
    elif attachment_ext in ('.ppt', '.pptx'):
        if aspose_slides is not None:
            ppt_file = aspose_slides.Presentation(attachment.file.path)
            options = aspose_slides.export.HtmlOptions()
            byte_stream = BytesIO()
            ppt_file.save(byte_stream, aspose_slides.export.SaveFormat.HTML, options)
            html_content = str(byte_stream.getvalue(), 'utf-8')
            result = remove_ppt_watermarks(html_content), True
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
            html_sheets[workbook.sheetnames[i]] = f'<div class="slide table_excel" id="slideslideIface{i+1}"> <hr> <h3 id="fsheet{id(workbook.sheetnames[i])}">{workbook.sheetnames[i]}</h3><hr> ' + current_sheet_html + '</div>'
        sheets = ''.join(f'{value}' for sheet_name, value in html_sheets.items())

        nav = '<ul>{}</ul>'.format(''.join(f'<li class="excel_nav"><a href="#fsheet{id(sheet_name)}">{sheet_name}</a></li>'
                                               for sheet_name in html_sheets.keys()))
        workbook.close()
        result = (sheets + nav), True
    elif attachment_ext in ['.htm', '.html']:
        file = attachment.file.open(mode='rb').read().decode('utf8')
        return file.replace('</style>', '\ntd { overflow: hidden; }</style>'), False
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
        result = html_content, False
    elif attachment_ext == '.doc':
        if aspose_words is not None:
            doc_file = aspose_words.Document(attachment.file.path)
            byte_stream = BytesIO()
            doc_file.save(byte_stream, aspose_words.SaveFormat.DOCX)
            html_content = convert_to_html(byte_stream).value
            result = remove_doc_watermarks(html_content), False
    elif attachment_ext == '.docx':
        result = convert_to_html(attachment.file.path).value, False
    return result

def tex_gen(attachment):
    lines = ''
    temp = str(attachment.file)
    file1 = open(attachment.file.path, encoding="utf-8")

    for line in file1:
        lines += line

    pattern = r"#!(.*?)!#"
    matches = re.findall(pattern, lines)
    print(matches)
    lvl = {'Легкая': 0, 'Средняя': 1, 'Сложная': 2, 'Очень сложная': 3}
    if len(matches) > 0:
        # temp = 'attachments/contests/contest/18/temp1.tex'
        temp = attachment.dirname + '\\temp_tex_generate.tex'

        with open(temp, 'w', encoding='utf-8') as infile:

            for match in matches:
                match = match.split('/')

                try:
                    found_course = Course.objects.get(title_official=match[0])
                except Course.DoesNotExis:
                    pass
                try:
                    found_contest = Contest.objects.get(title=match[1], course=found_course)
                except Contest.DoesNotExist:
                    pass

                if match[-1].endswith('.tex'):
                    lines = re.sub(pattern, 'в разработке', lines, count=1)

                elif match[-1] in lvl:

                    # found_course = Course.objects.get(title_official=match[0])
                    # found_contest = Contest.objects.get(title=match[1], course=found_course)
                    found_problem = Problem.objects.filter(difficulty=lvl[f'{match[2]}'], contest=found_contest)
                    random_problem = random.randint(0, len(found_problem) - 1)

                    try:
                        lines = re.sub(pattern, found_problem[random_problem].description, lines, count=1)
                    except re.error:
                        start_index = lines.find("#!") + 2
                        end_index = lines.find("!#", start_index)
                        text_to_replace = lines[start_index:end_index]
                        new_text = found_problem[random_problem].description
                        lines = lines.replace("#!" + text_to_replace + "!#", new_text, 1)

                else:
                    # found_course = Course.objects.get(title_official=match[0])
                    # found_contest = Contest.objects.get(title=match[1], course=found_course)

                    found_problem = Problem.objects.filter(title=match[2], contest=found_contest)

                    try:
                        lines = re.sub(pattern, found_problem[0].description, lines, count=1)
                    except re.error:
                        start_index = lines.find("#!") + 2
                        end_index = lines.find("!#", start_index)
                        text_to_replace = lines[start_index:end_index]
                        new_text = found_problem[0].description
                        lines = lines.replace("#!" + text_to_replace + "!#", new_text, 1)

            for line in lines:
                infile.write(line)

            start_index = temp.find("upload") + 7
            temp = temp[start_index:].replace('\\', '/')

    return temp
