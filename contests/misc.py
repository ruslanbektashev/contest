class Status:
    OK = 'OK'
    WA = 'WA'
    TF = 'TF'
    NA = 'NA'
    CE = 'CE'
    RE = 'RE'
    FE = 'FE'
    SF = 'SF'
    TL = 'TL'
    ML = 'ML'
    
    UN = 'UN'

    EX = 'EX'
    GO = 'GO'
    SA = 'SA'
    PO = 'PO'


# TODO: remove after squashing migrations
def submission_attachment_path(instance, filename):
    return ""


def lesson_attachment_path(instance, filename):
    return ""
