from django import forms
from django.conf import settings
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models
from djorm_pgarray.fields import ArrayField

import utils
import widgets


class TagsInputField(forms.ModelMultipleChoiceField):
    widget = widgets.TagsInputWidget

    def __init__(self, queryset, **kwargs):
        self.create_missing = kwargs.pop('create_missing', False)
        self.mapping = kwargs.pop('mapping', None)
        super(TagsInputField, self).__init__(queryset, **kwargs)
        self.widget.mapping = self.get_mapping()

    def get_mapping(self):
        if not self.mapping:
            self.mapping = mapping = utils.get_mapping(self.queryset)
            mapping['queryset'] = self.queryset
            mapping['create_missing'] = (
                self.create_missing
                or mapping.get('create_missing', False)
            )

        return self.mapping

    def clean(self, value):
        mapping = self.get_mapping()
        fields = mapping['fields']
        filter_func = mapping['filter_func']
        join_func = mapping['join_func']
        split_func = mapping['split_func']

        values = dict(
            join_func(v)[::-1] for v in self.queryset
            .filter(**filter_func(value))
            .values('pk', *fields)
        )
        missing = set(value) - set(values)
        if missing:
            if mapping['create_missing']:
                for v in value:
                    if v in missing:
                        o = self.queryset.model(**split_func(v))
                        o.clean()
                        o.save()
                        values[v] = o.pk
            else:
                raise ValidationError(self.error_messages['invalid_choice']
                                      % ', '.join(missing))

        ids = []
        for v in value:
            ids.append(values[v])

        return forms.ModelMultipleChoiceField.clean(self, ids)


class AdminTagsInputField(TagsInputField):
    widget = widgets.AdminTagsInputWidget


class TagsInputArrayField(ArrayField):
    """
    Extension of djorm_pgarray to override
    the default FormField
    """
    __metaclass__ = models.SubfieldBase

    def formfield(self, **params):
        params.setdefault('form_class', TagsInputFormArrayField)
        return super(TagsInputArrayField, self).formfield(**params)


class TagsInputFormArrayField(TagsInputField, TagsInputArrayField):
    """
    Mixin that creates the tags input field mixed with
    pgarray we need for the field Company.classes
    """
    def __init__(self, queryset=None, max_length=None, min_length=None, delim=None,
                 *args, **kwargs):
        self.create_missing = kwargs.pop('create_missing', False)
        self.mapping = kwargs.pop('mapping', None)

        if delim is not None:
            self.delim = delim
        else:
            self.delim = ','
        super(TagsInputFormArrayField, self).__init__(queryset, *args, **kwargs)
        self.widget.mapping = self.get_mapping()

    def clean(self, value):
        # Checks settings to see if we have an m2m or arrayfield option
        tag_model_option = getattr(settings, 'TAGS_INPUT_OPTIONS', False)

        if tag_model_option['arrayfield_model']:
            return value

        mapping = self.get_mapping()
        fields = mapping['fields']
        filter_func = mapping['filter_func']
        join_func = mapping['join_func']
        split_func = mapping['split_func']

        values = dict(
            join_func(v)[::-1] for v in self.queryset
            .filter(**filter_func(value))
            .values('pk', *fields)
        )
        missing = set(value) - set(values)
        if missing:
            if mapping['create_missing']:
                for v in value:
                    if v in missing:
                        o = self.queryset.model(**split_func(v))
                        o.clean()
                        o.save()
                        values[v] = o.pk
            else:
                raise ValidationError(self.error_messages['invalid_choice']
                                      % ', '.join(missing))

        ids = []
        for v in value:
            ids.append(values[v])

        return forms.ModelMultipleChoiceField.clean(self, ids)

    class Media:
        css = {
            'all': (
                'tags_input/static/css/jquery.tagsinput.css',
                'tags_input/static/css/base/jquery.ui.all.css',
            ),
        }
        js = (
            'tags_input/static/js/jquery.tagsinput.js',
            'tags_input/static/js/jquery-ui-18.1.16.min.js',
        )
