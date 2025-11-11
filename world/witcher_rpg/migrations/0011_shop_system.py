# Migration to add shop system
# Adds Shop, ShopInventory, ShopTransaction, and ShopRestockRule models

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0013_defaultobject_alter_objectdb_id_defaultcharacter_and_more'),
        ('witcher_rpg', '0010_social_combat_system'),
    ]

    operations = [
        # Create Shop model
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the shop', max_length=200)),
                ('shop_type', models.CharField(
                    choices=[
                        ('weaponsmith', 'Weaponsmith - Swords, axes, crossbows'),
                        ('armorsmith', 'Armorsmith - Armor and protective gear'),
                        ('jeweler', 'Jeweler - Jewelry, gems, luxury items'),
                        ('alchemist', 'Alchemist - Potions, oils, ingredients'),
                        ('general', 'General Store - Basic supplies and consumables'),
                        ('tailor', 'Tailor - Clothing and fashion'),
                        ('blacksmith', 'Blacksmith - Tools and basic weapons'),
                        ('enchanter', 'Enchanter - Magical items and scrolls'),
                    ],
                    help_text='Type of shop determines what items are stocked',
                    max_length=50
                )),
                ('tier', models.IntegerField(
                    choices=[
                        (1, 'Tier I - Poor quality, basic items'),
                        (2, 'Tier II - Common quality, decent selection'),
                        (3, 'Tier III - Good quality, wide selection'),
                        (4, 'Tier IV - Excellent quality, rare items'),
                    ],
                    default=1,
                    help_text='Investment tier determines quality and quantity of stock',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4)
                    ]
                )),
                ('faction', models.CharField(
                    choices=[
                        ('independent', 'Independent'),
                        ('nilfgaard', 'Nilfgaardian Empire'),
                        ('temeria', 'Temeria'),
                        ('redania', 'Redania'),
                        ('skellige', 'Skellige'),
                        ('witcher', 'Witcher Guild'),
                        ('mage', 'Mage Conclave'),
                        ('merchant_guild', 'Merchant Guild'),
                    ],
                    default='independent',
                    help_text='Faction affiliation affects available items',
                    max_length=50
                )),
                ('gold_reserves', models.IntegerField(
                    default=1000,
                    help_text='Gold available for buying items from players',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('markup_percentage', models.IntegerField(
                    default=150,
                    help_text='Sell price as percentage of base value (150 = 50% markup)',
                    validators=[
                        django.core.validators.MinValueValidator(100),
                        django.core.validators.MaxValueValidator(500)
                    ]
                )),
                ('buyback_percentage', models.IntegerField(
                    default=50,
                    help_text='Buy price as percentage of base value (50 = buy at half price)',
                    validators=[
                        django.core.validators.MinValueValidator(10),
                        django.core.validators.MaxValueValidator(100)
                    ]
                )),
                ('last_restock', models.DateTimeField(auto_now_add=True, help_text='When the shop was last restocked')),
                ('restock_interval_hours', models.IntegerField(
                    default=24,
                    help_text='Hours between automatic restocks',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('is_open', models.BooleanField(default=True, help_text='Whether the shop is currently open for business')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(
                    help_text='Room where this shop is located',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='shops',
                    to='objects.objectdb'
                )),
                ('owner', models.ForeignKey(
                    blank=True,
                    help_text='Player or NPC who owns this shop',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='owned_shops',
                    to='objects.objectdb'
                )),
                ('merchant', models.ForeignKey(
                    blank=True,
                    help_text='NPC merchant who runs the shop (susceptible to social combat)',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='merchant_shops',
                    to='objects.objectdb'
                )),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'location')},
            },
        ),

        # Create ShopInventory model
        migrations.CreateModel(
            name='ShopInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(
                    default=1,
                    help_text='Number of this item in stock',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('base_price', models.IntegerField(
                    default=100,
                    help_text='Base value of the item',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('is_special', models.BooleanField(
                    default=False,
                    help_text="Special/rare item that doesn't restock automatically"
                )),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='inventory',
                    to='witcher_rpg.shop'
                )),
                ('item_template', models.ForeignKey(
                    help_text='Template for the item being sold',
                    on_delete=django.db.models.deletion.CASCADE,
                    to='witcher_rpg.itemtemplate'
                )),
            ],
            options={
                'ordering': ['shop', 'item_template__name'],
                'unique_together': {('shop', 'item_template')},
            },
        ),

        # Create ShopTransaction model
        migrations.CreateModel(
            name='ShopTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(
                    choices=[
                        ('purchase', 'Purchase - Customer bought from shop'),
                        ('sale', 'Sale - Customer sold to shop'),
                    ],
                    max_length=20
                )),
                ('item_name', models.CharField(help_text='Name of item involved in transaction', max_length=200)),
                ('quantity', models.IntegerField(
                    default=1,
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('price_per_item', models.IntegerField(
                    help_text='Price per individual item',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('total_price', models.IntegerField(
                    help_text='Total transaction price',
                    validators=[django.core.validators.MinValueValidator(0)]
                )),
                ('social_discount', models.IntegerField(
                    default=0,
                    help_text='Percentage discount from social combat (0-100)'
                )),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('shop', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='transactions',
                    to='witcher_rpg.shop'
                )),
                ('customer', models.ForeignKey(
                    help_text='Player or NPC who made the transaction',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='shop_transactions',
                    to='objects.objectdb'
                )),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),

        # Create ShopRestockRule model
        migrations.CreateModel(
            name='ShopRestockRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_type', models.CharField(
                    choices=[
                        ('weaponsmith', 'Weaponsmith'),
                        ('armorsmith', 'Armorsmith'),
                        ('jeweler', 'Jeweler'),
                        ('alchemist', 'Alchemist'),
                        ('general', 'General Store'),
                        ('tailor', 'Tailor'),
                        ('blacksmith', 'Blacksmith'),
                        ('enchanter', 'Enchanter'),
                    ],
                    help_text='Which shop type this rule applies to',
                    max_length=50
                )),
                ('min_tier', models.IntegerField(
                    default=1,
                    help_text='Minimum shop tier required',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4)
                    ]
                )),
                ('max_tier', models.IntegerField(
                    default=4,
                    help_text='Maximum shop tier for this item',
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(4)
                    ]
                )),
                ('stock_chance', models.IntegerField(
                    default=50,
                    help_text='Percentage chance item appears during restock',
                    validators=[
                        django.core.validators.MinValueValidator(0),
                        django.core.validators.MaxValueValidator(100)
                    ]
                )),
                ('min_quantity', models.IntegerField(
                    default=1,
                    help_text='Minimum quantity when stocked',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('max_quantity', models.IntegerField(
                    default=5,
                    help_text='Maximum quantity when stocked',
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('allowed_factions', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of factions that can stock this (empty = all)'
                )),
                ('restricted_factions', models.JSONField(
                    blank=True,
                    default=list,
                    help_text='List of factions that cannot stock this'
                )),
                ('item_template', models.ForeignKey(
                    help_text='Item that can be stocked',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='restock_rules',
                    to='witcher_rpg.itemtemplate'
                )),
            ],
            options={
                'ordering': ['shop_type', 'min_tier', 'item_template__name'],
            },
        ),
    ]
