from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError, EqualTo, Regexp
from wtforms.widgets import TextArea
from models import User, Asset, Location, Asset_Category
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        Regexp(r'(?=.*[A-Z])', message='Password must contain at least one uppercase letter.'),
        Regexp(r'(?=.*[a-z])', message='Password must contain at least one lowercase letter.'),
        Regexp(r'(?=.*\d)', message='Password must contain at least one digit.'),
        Regexp(r'(?=.*[!@#$%^&*(),.?\":{}|<>])', message='Password must contain at least one special character.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    department = StringField('Department', validators=[Optional(), Length(max=100)])
    location_id = SelectField('Location', coerce=int, validators=[Optional()])
    submit = SubmitField('Register')
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.location_id.choices = [(0, 'Select Location')] + [(l.id, l.office_name) for l in Location.query.all()]
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class AssetForm(FlaskForm):
    asset_tag = StringField('Asset Tag', validators=[DataRequired(), Length(max=50)])
    name = StringField('Asset Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    serial_number = StringField('Serial Number', validators=[Optional(), Length(max=100)])
    purchase_date = DateField('Purchase Date', validators=[Optional()])
    purchase_price = DecimalField('Purchase Price', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('Status', choices=[
        ('Available', 'Available'),
        ('In Use', 'In Use'),
        ('Maintenance', 'Maintenance'),
        ('Retired', 'Retired')
    ], validators=[DataRequired()])
    assigned_to_user_id = SelectField('Assigned To', coerce=int, validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    location_id = SelectField('Location', coerce=int, validators=[DataRequired()])
    warranty_expiry = DateField('Warranty Expiry', validators=[Optional()])
    submit = SubmitField('Save Asset')
    
    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        self.assigned_to_user_id.choices = [(0, 'Not Assigned')] + [(u.id, u.username) for u in User.query.all()]
        self.category_id.choices = [(c.id, c.name) for c in Asset_Category.query.all()]
        self.location_id.choices = [(l.id, l.office_name) for l in Location.query.all()]
    
    def validate_asset_tag(self, asset_tag):
        if hasattr(self, 'original_asset_tag') and asset_tag.data == self.original_asset_tag:
            return
        
        asset = Asset.query.filter_by(asset_tag=asset_tag.data).first()
        if asset:
            raise ValidationError('Asset tag already exists. Please choose a different one.')
    
    def validate_purchase_date(self, purchase_date):
        if purchase_date.data and purchase_date.data > date.today():
            raise ValidationError('Purchase date cannot be in the future.')
    
    def validate_warranty_expiry(self, warranty_expiry):
        if warranty_expiry.data and self.purchase_date.data and warranty_expiry.data < self.purchase_date.data:
            raise ValidationError('Warranty expiry cannot be before purchase date.')

class LocationForm(FlaskForm):
    office_name = StringField('Office Name', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    country = StringField('Country', validators=[DataRequired(), Length(max=100)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Location')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    submit = SubmitField('Save Category')
    
    def validate_name(self, name):
        if hasattr(self, 'original_name') and name.data == self.original_name:
            return
        
        category = Asset_Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError('Category name already exists. Please choose a different one.')
