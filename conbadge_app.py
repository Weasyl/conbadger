from hashlib import sha1
import os.path

from flask import Flask, redirect, render_template, request, url_for
from PIL import Image

from conbadge import AvatarFetchError, weasyl_badge


upscaling = {
    'antialias': Image.ANTIALIAS,
    'bilinear': Image.BILINEAR,
    'bicubic': Image.BICUBIC,
    'nearest': Image.NEAREST,
}

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def generate_badge():
    username = request.form['username']
    upscale_method = upscaling.get(
        request.form.get('upscaling'), Image.ANTIALIAS)
    try:
        badge = weasyl_badge(username, upscale_method)
    except AvatarFetchError, e:
        error = 'Weasyl reported an error: %(text)s' % e.args[0]
        return render_template('index.html', error=error)
    username_sha = sha1(username.encode('utf-8')).hexdigest()
    badge_path = 'badges/%s.png' % (username_sha,)
    badge.save(os.path.join('static', badge_path))
    return redirect(url_for('static', filename=badge_path))
