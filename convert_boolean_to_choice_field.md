# Convert BooleanField to CharField with choices

I recently ran into a situation where I had a `BooleanField` that had to be converted to a `CharField` with three 
choices (Yes, No, and Maybe). With the django migration system it would be a trivial change to make, however, the 
feature has been in use for some time now and I wanted to preserve the original state and name of the boolean field 
when performing the migration.

For this example I'll use a model called `Invite`. It's a rather simple implementation of an invitation sent to someone
where we expect the recipient to RSVP yes or no whether they would be attending or not. In this feature we will add the
ability to also RSVP "Maybe" instead of just yes or no.

For the invitations where a recipient has RSVPd "yes", we need to preserve that they will be attending while ensuring
that any new invitations created default to "Maybe". Additionally we also want to be able to roll back the changes if
we ever need to.

This will involve creating a temporary field, saving the existing state in the temporary field, altering the
original field to have the desired choices, updating the state of the original field, and lastly removing the temporary
field.

This is the code that we'll be starting with:

`invite/models.py5

```python
from django.db import models


class Invite(models.Model):
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    rsvp_status = models.BooleanField(default=False) # Field to be updated

    def __str__(self) -> str:
        return f"{self.email} - {self.rsvp_status}"
```
This is where we want to end up:

```python
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

## Step 1: Creating a temporary field

Lets start by defining the available choices for the RSVP status

```python
class RSVPChoices(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"
    MAYBE = "maybe", "Maybe"

```

Next we need to add a temporary field that we will use to do the initial setup of our updated rsvp status field. This
temporary field will later be switched out with the original field and it therefore needs to match the structure of
the end result. Well, almost match. For the time being we need to make the field nullable and allow it to be blank. The
reason for this is... (TODO: Add reason)

I'll call this field `temp_rsvp_status`.

Updated code thus far:

```python
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

Create a migration...

```bash
python manage.py makemigrations
```

The migration should look something like this:

```python
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

Go ahead and apply the migration if you want and have a look at the model in the django backend. You should see the new
field with a dropdown contains all the choice options we specified. Don't make changes to the model in the backend.

```bash
python manage.py migrate
```

## Step 2: Save the existing state in the temporary field

WARNING: This is where it starts to get a bit more tricky.

Now that we have the temporary field, we can go ahead and update it to match the state of the existing rsvp field. We
want "yes" to be selected if the existing rsvp status is ticked and "Maybe" if it is not. 

To do this we need to create an empty migration where we will handel that logic ourselves. For that we'll use the 
following command:

```bash
python manage.py makemigrations <app_name> --empty --name <name_for_the_migration>
```

The `<app_name>` is the name of the app that this model lives in. Read more on django apps in the docs (TODO: Add link)
The `<name_for_the_migration>` is just a descriptive name for the migration file.

The full command in our case:

```bash
python manage.py makemigrations invite --empty --name copy_rsvp_status_details_to_temp
```

Check your migrations folder in the specified app. You should see a migration that looks something like this:

```python
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invite', '0002_invite_temp_rsvp_status'),
    ]

    operations = [
    ]
```

We want to be able to apply the migrations while also being able to still unapply the migrations as well. We need
to tell Django how to do that with 2 seperate functions. These functions I'll call `copy_forwards` and `copy_backwards`,
however, the names are up to you.

```python
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

You might have noticed the `apps` and `schema_editor` parameters to each of the functions. TODO: Add reason for them

These functions are rather simple and all they need to do is get the model and then copy the state beween the two 
fields. It will be easier to understand by reading the code:


```python
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
    # to false. exclude is used instead of filter because we want to catch 
    # both "no" and "maybe". I.e. anything that is not "yes"
    Invite.objects.exclude(temp_rsvp_status="yes").update(rsvp_status=False)

```

I think the code is self-explanitory. When we migrate "forwards" (apply the migration) we update the temporary rsvp 
status field to match the desired state based on the existing rsvp status field. When we migration "backwards"
(unaply the migration) we do the oposite essentially reversing the states.

The last thing we need to do in this step is to tell Django to run our functions when working with our new migration.
We do that by updating the `operations` list at the bottom of the file.

```python
operations = [
    migrations.RunPython(copy_forwards, copy_backwards)
]
```

Full code example:

```python
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
    # to false. exclude is used instead of filter because we want to catch 
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

We can apply the migration. You will see that the temporary rsvp status field has been update to match our existing
field. `True -> Yes | False -> Maybe`

```bash
python manage.py migrate
```

## Step 3: Alter the original field

With our copy logic in place we now need to swap the original rsvp field with the new one. For this we will create
another empty migration and write some custom rename logic.

```bash
python manage.py makemigrations invite --empty --name swap_rsvp_status_with_temp
```

This is another case where reading the code will make more sense than me explaining it

```python
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

## Step 4: Cleanup

Last we need to do some cleanup. In models.py, remove the temporary rsvp status and ensure that it matches
our migration.

```python
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
that we removed `old_rsvp_status`. This is good. It means that the step where we swapped the fields worked correctly.

```text
Migrations for 'invite':
  invite/migrations/0005_remove_invite_old_rsvp_status.py
    - Remove field old_rsvp_status from invite
```

Go ahead and apply the migration
```bash
python manage.py migrate
```

And that's it. Your new rsvp status checkbox should now reflect the state of the previous checkbox. Just how we want 
it.

You can access the code on GitHub. Head on over to the commits and see each step in its own commit.

