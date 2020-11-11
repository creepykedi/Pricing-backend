from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


def validate_okpd(val):
    seq_type = type(val)
    val = seq_type().join(filter(seq_type.isdigit, val))
    if len(val) > 12:
        raise ValidationError(
            _('Invalid value: %(value)s'),
            params={'value': val},
        )


def format_okpd(okpd):
    okpd = okpd.replace(".", "")
    length = len(str(okpd))
    for letter in range(12-length):
        okpd += "0"

    okpd = '.'.join(okpd[i:i + 3] for i in range(0, len(okpd), 3))
    return okpd