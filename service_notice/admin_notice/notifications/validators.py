import uuid

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_uuid(user_ids):
    for id in user_ids:
        try:
            uuid.UUID(id)
        except Exception:
            raise ValidationError(
                _('%(id)s is not UUID'),
                params={'id': id},
            )
