from django import forms


class BootstrapCheckboxSelect(forms.CheckboxSelectMultiple):
    template_name = 'forms/widgets/checkbox_select.html'
    option_template_name = 'forms/widgets/checkbox_option.html'


class BootstrapRadioSelect(forms.RadioSelect):
    template_name = 'forms/widgets/radio_select.html'
    option_template_name = 'forms/widgets/radio_option.html'
