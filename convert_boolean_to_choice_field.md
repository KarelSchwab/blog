I recently ran into a situation where I needed to convert a `BooleanField` (True / False) to a `CharField` with 
three choices—**Yes**, **No**, and **Maybe**. Django’s migration system makes schema changes straightforward, however, 
this feature has been in use for a while, and I wanted to preserve both the original state and the field name during 
the migration.

For this example I’ll use a model called `Invite`. It’s a simple model that represents an invitation where the 
recipient RSVPs to attending. Initially the RSVP was a boolean—Yes or No—and we’re adding a third option, Maybe, so 
we’ll migrate the field to a `CharField` with choices.

For invitations where a recipient has RSVP’d **Yes**, we need to preserve that they’re attending, while ensuring new 
invitations default to **Maybe**. We also want the option to roll the change back if needed.

We’ll do this in a few steps: create a temporary field, copy the existing values into it, alter the original field to 
a `CharField` with the new choices, and then lastly remove the temporary field.

This is the code that we'll be starting with:

```python title="invite/models.py"
from django.db import models


class Invite(models.Model):
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    rsvp_status = models.BooleanField(default=False) # Field to be updated

    def __str__(self) -> str:
        return f"{self.email} - {self.rsvp_status}"
```

This is what we want the result to be:


```python {title="invite/models.py"}
from django.db import models


class RSVPChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"


class Invite(models.Model):
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    rsvp_status = models.CharField(
        max_length=6, choices=RSVPChoices, default=RSVPChoices.MAYBE
    )

    def __str__(self) -> str:
        return f"{self.email} - {self.rsvp_status}"
```

## Step 1: Create a temporary field

We'll start by defining the available choices for the RSVP status using Django's `models.TextChoices` subclass. You can
read more about them in the [Django docs](https://docs.djangoproject.com/en/5.2/ref/models/fields/#enumeration-types) 

```python title="invite/models.py"
class RSVPChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"
```

Now that we’ve defined our choices, we’ll add a temporary field to stage the updated RSVP status. This temporary field 
should mirror the final field (same `max_length` and `choices`) so we can swap it out later (this will make sense soon). 
For now, we’ll also make it `nullable` and allow `blank` values. That avoids any NOT NULL or default value errors 
Django might raise during this migration. After backfilling the existing rows, we will enforce a default value.

Let's call this field `temp_rsvp_status` and update the code:


```python {title="invite/models.py"}
from django.db import models


class RSVPChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"


class Invite(models.Model):
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    rsvp_status = models.BooleanField(default=False)
    temp_rsvp_status = models.CharField(
        max_length=6, choices=RSVPChoices, null=True, blank=True
    )

    def __str__(self) -> str:
        return f"{self.email} - {self.rsvp_status}"
```

Create a migration to have our change take effect.


```bash
python manage.py makemigrations
```

The migration should look something like this:


```python {title="invite/migrations/0001_initial.py"}
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invite',
            name='temp_rsvp_status',
            field=models.CharField(
                blank=True, 
                choices=[
                    ('yes', 'Yes'), 
                    ('no', 'No'), 
                    ('maybe', 'Maybe')
                ], 
                max_length=6, 
                null=True
            ),
        ),
    ]
```

Go ahead and apply the migration and have a look at the model in the Django admin. You should see the new
field with a dropdown containing all the choices we specified.

**Note:** Don’t save changes in the admin yet. This is a temporary field that we’ll backfill and swap with the original 
field in the next steps, and editing it now could result in inconsistent data.


```bash
python manage.py migrate
```

## Step 2: Copy the existing state into the temporary field

This is where it starts to get a bit more tricky.

Now that we have the temporary field, we can update it to match the state of the existing `rsvp_status` field. We
want **Yes** to be selected if the existing `rsvp_status` is ticked (True) and **Maybe** if it is not (False). 

To do this we need to create an empty migration where we will handle that logic ourselves. For that we'll use the 
following command:


```bash
python manage.py makemigrations <app_name> --empty --name <name_for_the_migration>
```

The `<app_name>` is the name of the app that this model lives in. Read more on Django apps in 
the [docs](https://docs.djangoproject.com/en/5.2/ref/applications/#module-django.apps)

The `<name_for_the_migration>` is just a descriptive name for the migration file.

The full command in our case:

```bash
python manage.py makemigrations invite --empty --name copy_rsvp_status_details_to_temp
```

Check your migrations folder in the specified app. We should have an empty migration that looks something like this:


```python {title="invite/migrations/0002_invite_temp_rsvp_status.py"}
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0002_invite_temp_rsvp_status'),
    ]

    operations = [
    ]
```

We want this migration to be reversible. That means defining two separate functions, one for migrating **forwards** 
and one for **backwards**. Let's call them `copy_forwards` and `copy_backwards`(the names don’t matter).


```python {title="invite/migrations/0002_invite_temp_rsvp_status.py"}
from django.db import migrations

def copy_forwards(apps, schema_editor):
    """
    Used when applying the migration
    """
    pass


def copy_backwards(apps, schema_editor):
    """
    Used when unapplying the migration
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0002_invite_temp_rsvp_status'),
    ]

    operations = [
    ]
```

You might have noticed the `apps` and `schema_editor` parameters to each of the functions. I won't go into too much 
detail about it but `apps` gives you access to *Django's historical app registry*. This lets us "travel back in 
time" and load our model in the state when the migration takes place and not our current version of the model. 
`schema_editor`, on the other hand, is *Django's backend-aware DDL helper*. It can be used when writing custom 
operations to execute DDL or SQL safely. We won't be using it for this example.

These functions are rather simple and all they need to do is get the model and then copy the state between the two 
fields. It will be easier to understand by reading the code:


```python {title="invite/migrations/0002_invite_temp_rsvp_status.py"}
def copy_forwards(apps, schema_editor):
    """
    Used when applying the migration
    """
    # We get the model: get_model(<app_name>, <model_name>)
    Invite = apps.get_model("invite", "Invite")

    # Wherever the rsvp_status is True (checkbox ticked), set the temporary
    # field to "yes"
    Invite.objects.filter(rsvp_status=True).update(temp_rsvp_status="yes")

    # Wherever the rsvp_status is False (checkbox not ticked), set the temporary
    # field to "maybe" (our default)
    Invite.objects.filter(rsvp_status=False).update(temp_rsvp_status="maybe")


def copy_backwards(apps, schema_editor):
    """
    Used when unapplying the migration
    """
    # We get the model: get_model(<app_name>, <model_name>)
    Invite = apps.get_model("invite", "Invite")

    # Wherever the temp_rsvp_status is set to "yes" change it back to True
    Invite.objects.filter(temp_rsvp_status="yes").update(rsvp_status=True)

    # Wherever the temp_rsvp_status is set to "no" or "maybe" change it back
    # to False. exclude is used instead of filter because we want to catch 
    # both "no" and "maybe". I.e. anything that is not "yes"
    Invite.objects.exclude(temp_rsvp_status="yes").update(rsvp_status=False)
```

The code is self-explanatory. When we migrate **forwards** (apply the migration), we update the temporary RSVP field 
to the desired value based on the existing boolean field. When we migrate **backwards** (unapply/rollback), we do the 
opposite, restoring the original boolean values.

The last thing we need to do in this step is to tell Django to run our functions. We do that by updating the 
`operations` list at the bottom of the file and adding the `RunPython` operation. You can read more about 
it in the [django docs](https://docs.djangoproject.com/en/5.2/howto/writing-migrations/#how-to-create-database-migrations)

```python {title="invite/migrations/0002_invite_temp_rsvp_status.py"}
operations = [
    migrations.RunPython(copy_forwards, copy_backwards)
]
```

Full code example:

```python {title="invite/migrations/0002_invite_temp_rsvp_status.py"}
from django.db import migrations

def copy_forwards(apps, schema_editor):
    """
    Used when applying the migration
    """
    # We get the model: get_model(<app_name>, <model_name>)
    Invite = apps.get_model("invite", "Invite")

    # Wherever the rsvp_status is True (checkbox ticked), set the temporary
    # field to "yes"
    Invite.objects.filter(rsvp_status=True).update(temp_rsvp_status="yes")

    # Wherever the rsvp_status is False (checkbox not ticked), set the temporary
    # field to "maybe" (our default)
    Invite.objects.filter(rsvp_status=False).update(temp_rsvp_status="maybe")


def copy_backwards(apps, schema_editor):
    """
    Used when unapplying the migration
    """
    # We get the model: get_model(<app_name>, <model_name>)
    Invite = apps.get_model("invite", "Invite")

    # Wherever the temp_rsvp_status is set to "yes" change it back to True
    Invite.objects.filter(temp_rsvp_status="yes").update(rsvp_status=True)

    # Wherever the temp_rsvp_status is set to "no" or "maybe" change it back
    # to False. exclude is used instead of filter because we want to catch 
    # both "no" and "maybe". I.e. anything that is not "yes"
    Invite.objects.exclude(temp_rsvp_status="yes").update(rsvp_status=False)


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0002_invite_temp_rsvp_status'),
    ]

    operations = [
        migrations.RunPython(copy_forwards, copy_backwards)
    ]
```

Go ahead and apply the migration. If you go to the Django admin you will see that the temporary RSVP status field has 
been updated to match our existing RSVP field. **True** has been mapped to **Yes** while **False** to **Maybe**.

```bash
python manage.py migrate
```

## Step 3: Alter the original field

With our copy logic in place we now need to swap the original RSVP field with the new one. For this we will create
another empty migration and write some custom rename logic.

```bash
python manage.py makemigrations invite --empty --name swap_rsvp_status_with_temp
```

This is another case where reading the code will make more sense than me explaining it.

```python {title="invite/migrations/0003_copy_rsvp_status_details_to_temp.py"}
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0003_copy_rsvp_status_details_to_temp'),
    ]

    operations = [
        # Rename the existing field to something else so we can free
        # up its name (Will be deleted in next migration)
        migrations.RenameField(
            model_name="invite",
            old_name="rsvp_status",
            new_name="old_rsvp_status"
        ),
        # Rename the temporary rsvp status field to the original name
        migrations.RenameField(
            model_name="invite",
            old_name="temp_rsvp_status",
            new_name="rsvp_status"
        ),
        # Have the new rsvp status field not be nullable or blank by adding
        # a default and blank=False
        migrations.AlterField(
            model_name="invite",
            name="rsvp_status",
            field=models.CharField(
                max_length=6, 
                choices=[('yes', 'Yes'), ('no', 'No'), ('maybe', 'Maybe')],
                default="maybe",
                blank=False
            ),
        ),
    ]
```

```bash
python manage.py migrate
```

## Step 4: Cleanup, remove the temporary field

Last we need to do some cleanup. Remove the temporary RSVP status field and ensure that the constraints match that of 
our migration.

```python {title="invite/models.py"}
from django.db import models


class RSVPChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"


class Invite(models.Model):
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    rsvp_status = models.CharField(
        max_length=6, choices=RSVPChoices, default=RSVPChoices.MAYBE, blank=False
    )

    def __str__(self) -> str:
        return f"{self.email} - {self.rsvp_status}"
```

Make the migrations one last time:

```bash
python manage.py makemigrations
```

You should see something like this printed in the terminal. Note how we removed `temp_rsvp_status` but it shows us 
that we removed `old_rsvp_status`. This is good. It means that the step where we swapped the fields worked as expected.

```text
Migrations for 'invite':
  invite/migrations/0005_remove_invite_old_rsvp_status.py
    - Remove field old_rsvp_status from invite
```

Go ahead and apply the migration

```bash
python manage.py migrate
```

And that's it. Your new RSVP status choice should now reflect the state of the previous checkbox. Just how we want 
it.

You can access the code on [GitHub](https://github.com/KarelSchwab/boolean_to_choice_field). Head on over to the 
`commits` to see each step in its own commit.
