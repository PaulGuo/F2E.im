#
# Copyright (c) 2008 Daniel Truemper truemped@googlemail.com
#
# forms.py 31-Jul-2011
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# under the License.
#
#
"""
.. _WTForms: http://wtforms.simplecodes.com/

A simple wrapper for WTForms_.

Basically we only need to map the request handler's `arguments` to the 
`wtforms.form.Form` input. Quick example::

    from wtforms import TextField, validators
    from tornadotools.forms import Form

    class SampleForm(Form):
        username = TextField('Username', [
            validators.Length(min=4, message="Too short")
            ])

        email = TextField('Email', [
            validators.Length(min=4, message="Not a valid mail address"),
            validators.Email()
            ])

Then, in the `RequestHandler`::

    def get(self):
        form = SampleForm(self)
        if form.validate():
            # do something with form.username or form.email
            pass
        self.render('template.html', form=form)
"""
from wtforms import Form


class Form(Form):
    """
    `WTForms` wrapper for Tornado.
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        """
        Wrap the `formdata` with the `TornadoInputWrapper` and call the base
        constuctor.
        """
        self._handler = formdata
        super(Form, self).__init__(TornadoInputWrapper(formdata),
            obj=obj, prefix=prefix, **kwargs)

    def _get_translations(self):
        return TornadoLocaleWrapper(self._handler.get_user_locale())


class TornadoInputWrapper(object):

    def __init__(self, handler):
        self._handler = handler

    def __iter__(self):
        return iter(self._handler.request.arguments)

    def __len__(self):
        return len(self._handler.request.arguments)

    def __contains__(self, name):
        return (name in self._handler.request.arguments)

    def getlist(self, name):
        return self._handler.get_arguments(name)


class TornadoLocaleWrapper(object):

    def __init__(self, locale):
        self.locale = locale

    def gettext(self, message):
        return self.locale.translate(message) if self.locale else message

    def ngettext(self, message, plural_message, count):
        return self.locale.translate(message, plural_message, count) if self.locale else message
