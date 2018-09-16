import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from dasi.models import Sequence

bp = Blueprint('sequences', __name__, url_prefix='/sequences')


@bp.route('/')
def index():
    seqs = Sequence.query.all()
    return render_template('sequences/index.html', sequences=seqs)
