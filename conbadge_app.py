# Copyright (c) Weasyl LLC
# See COPYING for details.

import os.path

from flask import Flask, abort, redirect, render_template, request, url_for
from PIL import Image

from conbadge import AvatarFetchError, weasyl_badge, weasyl_sysname

# Valid upscaling options for resizing a user's avatar.
upscaling = {
    'antialias': Image.ANTIALIAS,
    'bilinear': Image.BILINEAR,
    'bicubic': Image.BICUBIC,
    'nearest': Image.NEAREST,
}

app = Flask(__name__)

def badge_path(sysname):
    """Returns a path pointing to the badge for a given sysname."""
    return os.path.join('static', 'badges', sysname + '.png')

def badge_url(sysname):
    """Returns a URL pointing to the badge for a given sysname."""
    return url_for('static', filename=os.path.join('badges', sysname + '.png'))

@app.route('/')
def index():
    """Serves the rendered index template."""
    return render_template('index.html')

@app.route('/', methods=['POST'])
def generate_badge():
    """Renders a badge for a user and redirects to a page displaying it."""
    username = request.form['username']
    upscale_method = upscaling.get(
        request.form.get('upscaling'), Image.ANTIALIAS)
    try:
        badge = weasyl_badge(username, upscale_method)
    except AvatarFetchError, e:
        error = 'Weasyl reported an error: %(text)s' % e.args[0]
        return render_template('index.html', error=error)
    sysname = weasyl_sysname(username)
    badge.save(badge_path(sysname))
    return redirect(url_for('show_badge', sysname=sysname))

@app.route('/badge/<sysname>')
def show_badge(sysname):
    """Show the given user's badge."""
    path = badge_path(sysname)
    if not os.path.exists(path):
        abort(404)
    return render_template('show-badge.html',
                           sysname=sysname, badge_url=badge_url(sysname))
