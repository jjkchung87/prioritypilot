from wtforms import SelectField, StringField, TextAreaField, PasswordField, DateField, SelectMultipleField, IntegerField, SubmitField, ValidationError
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, Optional, Length, Email, NumberRange, email_validator
import email_validator
from datetime import datetime

class LowercaseField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].lower()
        else:
            self.data = ''


class SignUpForm(FlaskForm):
    """Form for new user sign ups."""
    first_name = StringField('First Name',validators=[InputRequired()])
    last_name = StringField('Last Name',validators=[InputRequired()])
    username = LowercaseField('Username',validators=[InputRequired(), Length(max=20)])
    email = StringField('Email',validators=[Email()])
    password = PasswordField('Password',validators=[InputRequired(), Length(min=6)])
    profile_url = StringField('(Optional) Image URL', validators=[Optional()])

class LoginForm(FlaskForm):
    """Form for user to log in."""
    username = LowercaseField('Username',validators=[InputRequired(), Length(max=20)])
    password = PasswordField('Password',validators=[InputRequired(), Length(min=6)])

class UserUpdateForm(FlaskForm):
    """Form to update existing user details"""
    first_name = StringField('First Name',validators=[Optional()])
    last_name = StringField('Last Name',validators=[Optional()])
    username = LowercaseField('Username',validators=[Optional(), Length(max=20)])
    email = StringField('Email',validators=[Optional(),Email()])
    profile_url = StringField('(Optional) Image URL', validators=[Optional()])
    new_password = PasswordField('New Password (Optional)',validators= [Optional(),Length(min=6) ])
    old_password = PasswordField('Old Password (Required)',validators=[InputRequired(), Length(min=6)])
    

class CreateLeagueForm(FlaskForm):
    """Form to create a new league"""
    league_name= LowercaseField('League Name', validators=[InputRequired()])
    start_date= DateField('Start Date', validators=[InputRequired()])
    end_date= DateField('End Date', validators=[InputRequired()])
    privacy = SelectField('Private or Public', choices=[('private','Private'),('public','Public')], validators=[InputRequired()])
    max_teams = IntegerField('Maximum Number of Teams', validators=[NumberRange(min=1, max=10)])
    golfer_count = IntegerField('Team Size', validators=[NumberRange(min=1, max=10)])

    def validate_end_date(form, field):
        if field.data <= form.start_date.data:
            raise ValidationError("End date must be after start date.")
        
    def validate_start_date(form, field):
        if field.data < datetime.utcnow().date():
            raise ValidationError("Start date cannot be in the past.")

    # def validate(self):
    #     if not super(CreateLeagueForm, self).validate():
    #         return False

    #     if self.start_date.data >= self.end_date.data:
    #         self.end_date.errors.append("End date must be after start date.")
    #         return False

    #     return True


class JoinPrivateLeagueForm(FlaskForm):
    """Form to join a private league"""
    league_name= LowercaseField('League Name', validators=[InputRequired()])
    entry_code = StringField('Entry Code', validators=[InputRequired()])

class JoinPublicLeagueForm(FlaskForm):
    """Form to join a public league"""

    league_name = SelectField("Choose League", coerce=int)

    def set_choices(self, public_leagues):
        self.league_name.choices = [(league.id, league.league_name) for league in public_leagues]

class CreateTeamForm(FlaskForm):
    """Form to create a new team"""

    team_name = LowercaseField('Team Name', validators=[InputRequired()])


class DraftGolfersForm(FlaskForm):
    """Form to draft golfers"""

    golfer = SelectField('Select a Golfer', validators=[InputRequired()])



    
