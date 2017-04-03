from django.db import models
from core.models.donkey_user import DonkeyUser


class Connector(models.Model):
    donkey_user = models.OneToOneField(DonkeyUser)
    bulletin_board_id_str = models.TextField(null=True)

    def set_bulletinboard_id(self, bulletinboard_id):
        value = self.bulletin_board_id_str
        if not value:
            value = format('{},'.format(bulletinboard_id))
        else:
            value += format('{},'.format(bulletinboard_id))

        self.bulletin_board_id_str = value
        self.save()
