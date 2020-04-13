from pagedown.widgets import PagedownWidget


class MyNewWidget(PagedownWidget):
    template_name = 'accounts/comment/comment_widget.html'
