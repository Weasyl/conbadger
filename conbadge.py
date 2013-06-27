# Copyright (c) Weasyl LLC
# See COPYING for details.

from fractions import Fraction
from cStringIO import StringIO

from PIL import Image, ImageDraw, ImageFont
import qrcode
import requests

# Open the font, background image, and logo stamp
museo = ImageFont.truetype('Museo500-Regular.otf', 424)
badge_back = Image.open('badge-back.png')
logo_stamp = Image.open('logo-stamp.png')

# Sane sizes and offsets to be used when generating the badge.
qr_size = 975, 975
qr_offset = 75, 75
name_color = 6, 155, 192
text_bounds = 735, 125
text_offset = 365, 1155
avatar_bounds = 282, 282
avatar_offset = 49, 1131


class AvatarFetchError(Exception):
    """Exception class for problems fetching the user's avatar."""
    pass


def draw_text(text, color, fit_size):
    """
    Draw text within an image to fit a given size and return the image.

    Arguments:
    text: the text to draw.
    color: the color in which to draw the text.
    fit_size: a tuple containing size in which the text should fit.

    """
    text_size = museo.getsize(text)
    img = Image.new('RGBA', text_size, color + (0,))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, color + (255,), font=museo)
    width, height = img.size
    fit_width, fit_height = fit_size

    width_ratio = Fraction(width, fit_width)
    height_ratio = Fraction(height, fit_height)
    if width_ratio > height_ratio:
        new_size = fit_width, int(height / width_ratio)
    else:
        new_size = int(width / height_ratio), fit_height

    return img.resize(new_size, Image.ANTIALIAS)

def center(size, fit_size, offset):
    """
    Center a given area within another area at an offset.

    Arguments:
    size: a tuple containing the width and height of the area to be centered.
    fit_Size: a tuple containing the width and heigh of the area in which to 
    center 'size'
    offset: a tuple representing an x/y coordinate of the offset.

    """
    w, h = size
    fw, fh = fit_size
    x, y = offset
    return x + (fw - w) // 2, y + (fh - h) // 2

logo_pos = center(logo_stamp.size, qr_size, qr_offset)

def weasyl_sysname(target):
    """Return the Weasyl sysname for use in a URL for a given username."""
    return ''.join(i for i in target if i.isalnum()).lower()

def weasyl_badge(username, avatar_resizing=Image.ANTIALIAS):
    """
    Generate a badge image for a given username.

    This generates an image containing a QR code which will point to the user's
    Weasyl page.  It will also include their username and their user avatar.

    Arguments:
    username: the user requesting the badge.
    avatar_resizing: how to scale the user's avatar (defaults to antialiasing).
    
    """
    # Retrieve the user's avatar.
    r = requests.get(
        'https://www.weasyl.com/api/useravatar', params={'username': username})
    resp = r.json()
    if resp['error']['code'] != 0:
        raise AvatarFetchError(resp['error'])

    # Build the QR code for the user's page onto the backing.
    back = badge_back.copy()
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H, border=1)
    qr.add_data('https://weasyl.com/~%s' % (weasyl_sysname(username),))
    qr_mask = qr.make_image().resize(qr_size)
    back.paste((255, 255, 255, 255), qr_offset, qr_mask)
    back.paste(logo_stamp, logo_pos, logo_stamp)

    # Add the username text.
    text = draw_text(username, name_color, text_bounds)
    text_pos = center(text.size, text_bounds, text_offset)
    back.paste(text, text_pos, text)

    # Add the avatar last.
    avatar = Image.open(StringIO(requests.get(resp['avatar']).content))
    avatar = avatar.resize(avatar_bounds, avatar_resizing).convert('RGBA')
    back.paste(avatar, avatar_offset, avatar)

    return back
