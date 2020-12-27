# Generated by Django 3.1.4 on 2020-12-27 10:34

import apps.core.models
import apps.sales.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('materials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('state', django_fsm.FSMField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('PAST_DUE', 'Account Past Due'), ('INACTIVE', 'Inactive')], default='PENDING', max_length=50, verbose_name='Status')),
            ],
            options={
                'ordering': ['name'],
                'permissions': [('change_client_status', 'Can change status of client')],
            },
        ),
        migrations.CreateModel(
            name='ClientLocation',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('location_type', models.CharField(choices=[('RETAIL', 'Retail Location'), ('RDC', 'Distribution Center'), ('CORPORATE', 'Corporate Offices'), ('ACCOUNTING', 'Accounting Dept')], default='RDC', max_length=16, verbose_name='Location Type')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='sales.client')),
                ('served_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributes_to', to='sales.clientlocation')),
            ],
            options={
                'ordering': ['location_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='DeliveryMethod',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=24, verbose_name='Service')),
                ('lead_time', models.PositiveIntegerField(default=0)),
                ('cutoff_time', models.TimeField(blank=True, default=apps.sales.models.default_cutoff_time, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SaleOrder',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('invoice_id', models.CharField(default=apps.sales.models.increment_invoice_id, editable=False, max_length=8, unique=True, verbose_name='Invoice Number')),
                ('date', models.DateTimeField(default=datetime.date.today, verbose_name='Date placed')),
                ('date_delivery_scheduled', models.DateField(verbose_name='Scheduled Delivery Date')),
                ('date_order_release', models.DateField(blank=True, null=True, verbose_name='Order Release Date')),
                ('date_delivery_actual', models.DateField(blank=True, null=True, verbose_name='Actual Delivery Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('state', django_fsm.FSMField(choices=[('PENDING', 'Pending'), ('CANCELLED', 'Cancelled'), ('CANCELLED_PENALTY', 'Cancelled Late (Penalty)'), ('RELEASED', 'Released for Production'), ('COMMITTED', 'Committed for Production'), ('FULFILLED', 'Fulfilled'), ('FULFILLED_SHORT', 'Fulfilled (product short/complaint)')], default='PENDING', max_length=50, verbose_name='Status')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_orders', to='sales.client')),
                ('delivery_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sale_orders', to='sales.deliverymethod')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_orders', to='sales.clientlocation')),
            ],
            options={
                'ordering': ['date_delivery_scheduled'],
                'permissions': [('change_sales_order_status', 'Can change status of sales order')],
                'get_latest_by': ['date'],
            },
        ),
        migrations.CreateModel(
            name='SaleOrderLine',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('quantity', models.PositiveSmallIntegerField(default=0, verbose_name='Quantity')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_order_lines', to='materials.material')),
                ('sale_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='sales.saleorder')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.unitmeasurement')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientPreference',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('deliver_to_preference', models.CharField(choices=[('LOCATION', 'This Location'), ('RDC', 'Distribution Center'), ('CORPORATE', 'Corporate Offices'), ('ACCOUNTING', 'Accounting Dept')], default='RDC', max_length=16, verbose_name='Deliver Product to')),
                ('bill_to_preference', models.CharField(choices=[('LOCATION', 'This Location'), ('RDC', 'Distribution Center'), ('CORPORATE', 'Corporate Offices'), ('ACCOUNTING', 'Accounting Dept')], default='CORPORATE', max_length=16, verbose_name='Direct Invoices to')),
                ('client', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='sales.client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientLocationAddress',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('address_line_1', models.CharField(blank=True, max_length=64, null=True, verbose_name='Address Line 1')),
                ('address_line_2', models.CharField(blank=True, max_length=64, null=True, verbose_name='Address Line 2')),
                ('address_line_3', models.CharField(blank=True, max_length=64, null=True, verbose_name='Address Line 1')),
                ('address_city', models.CharField(blank=True, max_length=32, null=True, verbose_name='City')),
                ('address_state', models.CharField(choices=[('AL', 'Alabama '), ('AK', 'Alaska '), ('AZ', 'Arizona '), ('AR', 'Arkansas '), ('CA', 'California '), ('CO', 'Colorado '), ('CT', 'Connecticut '), ('DE', 'Delaware '), ('FL', 'Florida '), ('GA', 'Georgia '), ('HI', 'Hawaii '), ('ID', 'Idaho '), ('IL', 'Illinois '), ('IN', 'Indiana '), ('IA', 'Iowa '), ('KS', 'Kansas '), ('KY', 'Kentucky '), ('LA', 'Louisiana '), ('ME', 'Maine '), ('MD', 'Maryland '), ('MA', 'Massachusetts '), ('MI', 'Michigan '), ('MN', 'Minnesota '), ('MS', 'Mississippi '), ('MO', 'Missouri '), ('MT', 'Montana '), ('NE', 'Nebraska '), ('NV', 'Nevada '), ('NH', 'New Hampshire '), ('NJ', 'New Jersey '), ('NM', 'New Mexico '), ('NY', 'New York '), ('NC', 'North Carolina '), ('ND', 'North Dakota '), ('OH', 'Ohio '), ('OK', 'Oklahoma '), ('OR', 'Oregon '), ('PA', 'Pennsylvania '), ('RI', 'Rhode Island '), ('SC', 'South Carolina '), ('SD', 'South Dakota '), ('TN', 'Tennessee '), ('TX', 'Texas '), ('UT', 'Utah '), ('VT', 'Vermont '), ('VA', 'Virginia '), ('WA', 'Washington '), ('WV', 'West Virginia '), ('WI', 'Wisconsin '), ('WY', 'Wyoming ')], default='NY', max_length=2, verbose_name='State')),
                ('address_zipcode', models.CharField(blank=True, max_length=10, null=True, verbose_name='Zipcode')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='sales.clientlocation')),
            ],
            options={
                'verbose_name_plural': 'Client location addresses',
            },
        ),
        migrations.CreateModel(
            name='ClientContact',
            fields=[
                ('id', models.CharField(blank=True, default=apps.core.models.generate_ulid, editable=False, max_length=26, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('name', models.CharField(max_length=64, verbose_name='Name')),
                ('preferred_method', models.CharField(choices=[('MOBILE', 'via Mobile'), ('TELEPHONE', 'via Telephone'), ('FAX', 'via Fax'), ('EMAIL', 'via Email')], default='MOBILE', max_length=9, verbose_name='Preferred Contact Method')),
                ('contact_mobile', models.CharField(blank=True, max_length=64, null=True, verbose_name='Mobile')),
                ('contact_telephone', models.CharField(blank=True, max_length=64, null=True, verbose_name='Office Tel.')),
                ('contact_fax', models.CharField(blank=True, max_length=64, null=True, verbose_name='Fax')),
                ('contact_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='sales.clientlocation')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]