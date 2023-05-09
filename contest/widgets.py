from django import forms


class BootstrapSelectMixin:
    def __init__(self, attrs=None, choices=(), option_attrs=None):
        super().__init__(attrs, choices)
        self.option_attrs = option_attrs

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if self.option_attrs is not None:
            for data_attr, values in self.option_attrs.items():
                option['attrs'][data_attr] = values[getattr(option['value'], 'value', option['value'])]
        return option


class BootstrapSelect(BootstrapSelectMixin, forms.Select):
    pass


class BootstrapSelectMultiple(BootstrapSelectMixin, forms.SelectMultiple):
    pass


class BootstrapCheckboxSelect(forms.CheckboxSelectMultiple):
    template_name = 'forms/widgets/checkbox_select.html'
    option_template_name = 'forms/widgets/checkbox_option.html'


class BootstrapRadioSelect(forms.RadioSelect):
    template_name = 'forms/widgets/radio_select.html'
    option_template_name = 'forms/widgets/radio_option.html'


class OptionCheckboxSelect(forms.CheckboxSelectMultiple):
    template_name = 'forms/widgets/option_checkbox_select.html'
    option_template_name = 'forms/widgets/option_checkbox_option.html'


class OptionRadioSelect(forms.RadioSelect):
    template_name = 'forms/widgets/option_radio_select.html'
    option_template_name = 'forms/widgets/option_radio_option.html'
