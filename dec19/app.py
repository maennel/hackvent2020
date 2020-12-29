import enum
import pathlib
import tempfile
import dataclasses
from typing import Callable

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import fields, validators
from werkzeug import utils

import linting


app = Flask(__name__)
app.secret_key = b'Q.J\t\x0be\x0c\x90\x9aNV\x11\xa4i\xc1\xa3'
bootstrap = Bootstrap(app)


class InputForm(FlaskForm):

    contents = fields.TextAreaField('Paste a file:', render_kw={'rows': 15})
    uploaded = fields.FileField('Or upload your file here:')
    submit = fields.SubmitField()

    def validate_contents(self, field):
        if not self.contents.data and not self.uploaded.data:
            raise validators.ValidationError("Either paste or upload a file")

    def validate_uploaded(self, field):
        if self.uploaded.data and not utils.secure_filename(self.uploaded.data.filename):
            raise validators.ValidationError("Invalid filename")


class FileType(enum.Enum):

    docker = enum.auto()
    compose = enum.auto()
    env = enum.auto()


@dataclasses.dataclass
class FileTypeInfo:

    title: str
    ace_mode: str
    default_filename: str
    func: Callable


_FILETYPE_INFO = {
    FileType.docker: FileTypeInfo(
        title='Dockerfile',
        ace_mode='dockerfile',
        func=linting.lint_docker,
        default_filename='Dockerfile',
    ),

    FileType.compose: FileTypeInfo(
        title='docker-compose.yml',
        ace_mode='yaml',
        func=linting.lint_compose,
        default_filename='docker-compose.yml',
    ),

    FileType.env: FileTypeInfo(
        title='.env file',
        ace_mode='sh',  # close enough
        func=linting.lint_env,
        default_filename='dotenv.env',
    ),
}


@app.route('/')
def home():
    return render_template('home.html')


def _show_results(path, results, *, warn_both):
    for result in results.values():
        result.stdout = result.stdout.replace(f'{path.parent}/', '')
        result.stderr = result.stderr.replace(f'{path.parent}/', '')
    return render_template('output.html', results=results, warn_both=warn_both)


def _normalize_form_data(data):
    data = data.replace('\r\n', '\n')
    return data.rstrip('\n') + '\n'


def _post_form(form, info):
    data = form.data['contents']
    warn_both = False
    with tempfile.TemporaryDirectory() as tdir:
        if data.strip():
            warn_both = bool(form.data['uploaded'])
            path = pathlib.Path(tdir) / info.default_filename
            path.write_text(_normalize_form_data(data))
        else:
            uploaded = form.data['uploaded']
            filename = utils.secure_filename(uploaded.filename)
            path = pathlib.Path(tdir) / filename
            uploaded.save(path)
        results = info.func(path)
    return _show_results(path, results, warn_both=warn_both)


def _form_helper(filetype):
    info = _FILETYPE_INFO[filetype]

    form = InputForm()
    if form.validate_on_submit():
        return _post_form(form, info)

    return render_template(
        'form.html',
        title=info.title,
        form=form,
        render_kw={'data-mode': info.ace_mode},
    )


@app.route('/docker', methods=('GET', 'POST'))
def docker():
    return _form_helper(FileType.docker)


@app.route('/compose', methods=('GET', 'POST'))
def compose():
    return _form_helper(FileType.compose)


@app.route('/env', methods=('GET', 'POST'))
def env():
    return _form_helper(FileType.env)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
