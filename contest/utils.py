import enum

from django.conf import settings
from django.views.generic import TemplateView


class Status(enum.Enum):
    OK = 14  # Test Passed
    TF = 13  # Test Failed
    WA = 12  # Wrong Answer
    NA = 11  # No Answer

    TL = 10  # Time Limit Exceeded
    ML = 9   # Memory Limit Exceeded
    CL = 8   # Compilation Time Limit Exceeded
    SF = 7   # Segmentation Fault
    FE = 6   # Floating Point Error
    RE = 5   # Runtime Error

    CE = 4   # Compilation Error
    UE = 3   # Unicode Decode Error
    PE = 2   # Package Error
    EX = 1   # Unknown Exception

    UN = 0   # Undefined

    def __str__(self):
        return self.name


def diff(output, correct, precision=None, check_format=False):
    if check_format and len(output.splitlines()) != len(correct.splitlines()):
        return True  # number of lines differ
    out_tokens, cor_tokens = output.split(), correct.split()
    if len(out_tokens) != len(cor_tokens):
        return True  # number of tokens differ
    _precision = precision or 1e-5
    for out_token, cor_token in zip(out_tokens, cor_tokens):
        if out_token != cor_token:
            if precision is None:
                try:
                    if int(out_token) != int(cor_token):
                        return True  # int token differs
                    else:
                        continue
                except ValueError:
                    pass
            if check_format and len(out_token) != len(cor_token):
                return True  # token length differs
            try:
                if abs(float(out_token) - float(cor_token)) > _precision:
                    return True  # float token differs
            except ValueError:
                return True  # NaN token differs
    return False


class Sandbox:
    pass


def under_development(view):
    if settings.DEBUG:
        return view
    else:
        return TemplateView.as_view(template_name='under_development.html')


def transliterate(string):
    alphabet_ru_a = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    alphabet_ru_s = 'жйхцчшщыюя'
    translit_en_a = 'abvgdee_zi_klmnoprstuf________e__'
    translit_en_s = ['zh', 'y', 'kh', 'ts', 'ch', 'sh', 'sh', 'y', 'yu', 'ya']
    transtable = {ord(c): p for c, p in zip(alphabet_ru_a, translit_en_a)}
    transtable.update({ord(c): p for c, p in zip(alphabet_ru_s, translit_en_s)})
    return string.translate(transtable)
