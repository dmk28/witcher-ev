# Migration to update Witcher appearance mechanic
# Changes from -1 general penalty to situational +3 for seduction vs females (lore-accurate)

from django.db import migrations


def update_witcher_appearance(apps, schema_editor):
    """
    Update Witcher vocation appearance modifier.
    Remove general -1 penalty, add situational +3 for seduction vs females.
    """
    Vocation = apps.get_model('witcher_rpg', 'Vocation')

    try:
        witcher = Vocation.objects.get(name='witcher')
        # Remove general appearance penalty
        witcher.appearance_mod = 0
        witcher.save()
        print("Updated Witcher appearance_mod from -1 to 0 (situational +3 for seduction vs females)")
    except Vocation.DoesNotExist:
        print("Witcher vocation not found, skipping")


def reverse_witcher_appearance(apps, schema_editor):
    """
    Revert Witcher appearance to old -1 penalty.
    """
    Vocation = apps.get_model('witcher_rpg', 'Vocation')

    try:
        witcher = Vocation.objects.get(name='witcher')
        witcher.appearance_mod = -1
        witcher.save()
        print("Reverted Witcher appearance_mod to -1")
    except Vocation.DoesNotExist:
        print("Witcher vocation not found, skipping")


class Migration(migrations.Migration):

    dependencies = [
        ('witcher_rpg', '0004_biomemobtemplate_itemtemplate_bankstorage_currency_and_more'),
    ]

    operations = [
        migrations.RunPython(update_witcher_appearance, reverse_witcher_appearance),
    ]
