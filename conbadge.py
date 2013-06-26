from fractions import Fraction
from cStringIO import StringIO

from PIL import Image, ImageDraw, ImageFont
import qrcode
import requests


museo = ImageFont.truetype('Museo500-Regular.otf', 424)
badge_back = Image.open('badge-back.png')
logo_stamp = Image.open('logo-stamp.png')

qr_size = 975, 975
qr_offset = 75, 75
name_color = 6, 155, 192
text_bounds = 735, 125
text_offset = 365, 1155
avatar_bounds = 282, 282
avatar_offset = 49, 1131


class AvatarFetchError(Exception):
    pass


def draw_text(text, color, fit_size):
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
    w, h = size
    fw, fh = fit_size
    x, y = offset
    return x + (fw - w) // 2, y + (fh - h) // 2

logo_pos = center(logo_stamp.size, qr_size, qr_offset)

def weasyl_sysname(target):
  return ''.join(i for i in target if i.isalnum()).lower()

def weasyl_badge(username, avatar_resizing=Image.ANTIALIAS):
    r = requests.get(
        'https://www.weasyl.com/api/useravatar', params={'username': username})
    resp = r.json()
    if resp['error']['code'] != 0:
        raise AvatarFetchError(resp['error'])

    back = badge_back.copy()
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H, border=1)
    qr.add_data('https://weasyl.com/~%s' % (weasyl_sysname(username),))
    qr_mask = qr.make_image().resize(qr_size)
    back.paste((255, 255, 255, 255), qr_offset, qr_mask)
    back.paste(logo_stamp, logo_pos, logo_stamp)
    text = draw_text(username, name_color, text_bounds)
    text_pos = center(text.size, text_bounds, text_offset)
    back.paste(text, text_pos, text)

    avatar = Image.open(StringIO(requests.get(resp['avatar']).content))
    avatar = avatar.resize(avatar_bounds, avatar_resizing).convert('RGBA')
    back.paste(avatar, avatar_offset, avatar)

    return back
