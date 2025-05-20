from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField, TimeField, DateField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError

class OperatorForm(FlaskForm):
    operator_code = StringField('Operator Code', validators=[DataRequired(), Length(max=10)])
    operator_short_name = StringField('Operator Short Name', validators=[DataRequired(), Length(max=30)])
    operator_name_on_licence = StringField('Operator Name on Licence', validators=[DataRequired(), Length(max=100)])
    trading_name = StringField('Trading Name', validators=[DataRequired(), Length(max=100)])
    licence_number = StringField('Licence Number', validators=[DataRequired(), Length(max=20)])
    licence_classification = SelectField('Licence Classification', choices=[
        ('standardNational', 'Standard National'),
        ('standardInternational', 'Standard International'),
        ('restricted', 'Restricted')
    ], validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[DataRequired(), Length(max=100)])
    telephone = StringField('Telephone', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired(), Length(max=100)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=100)])
    address_line3 = StringField('Address Line 3', validators=[Optional(), Length(max=100)])
    town = StringField('Town', validators=[DataRequired(), Length(max=100)])
    postcode = StringField('Postcode', validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Save and continue')

class ServiceForm(FlaskForm):
    service_code = StringField('Service Code', validators=[DataRequired(), Length(max=20)])
    line_name = StringField('Line Name', validators=[DataRequired(), Length(max=10)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Service Description', validators=[DataRequired(), Length(max=1000)])
    origin = StringField('Origin', validators=[DataRequired(), Length(max=100)])
    destination = StringField('Destination', validators=[DataRequired(), Length(max=100)])
    wheelchair_accessible = BooleanField('Wheelchair Accessible')
    submit = SubmitField('Save and continue')

class StopForm(FlaskForm):
    atco_code = StringField('ATCO Code', validators=[Optional(), Length(max=20)])
    naptan_code = StringField('NaPTAN Code', validators=[Optional(), Length(max=10)])
    common_name = StringField('Common Name', validators=[DataRequired(), Length(max=100)])
    indicator = StringField('Indicator (e.g. "outside", "opposite")', validators=[Optional(), Length(max=50)])
    locality = StringField('Locality', validators=[DataRequired(), Length(max=100)])
    longitude = StringField('Longitude', validators=[Optional()])
    latitude = StringField('Latitude', validators=[Optional()])
    travel_time_to_next = StringField('Travel Time to Next Stop (minutes)', validators=[Optional()])
    submit = SubmitField('Save and continue')
    
class AddStopForm(FlaskForm):
    add_stop = SubmitField('Add Another Stop')

class RouteForm(FlaskForm):
    route_id = StringField('Route ID', validators=[DataRequired(), Length(max=20)])
    description = StringField('Route Description', validators=[DataRequired(), Length(max=100)])
    direction = SelectField('Direction', choices=[
        ('outbound', 'Outbound'),
        ('inbound', 'Inbound')
    ], validators=[DataRequired()])
    submit = SubmitField('Save and continue')

class JourneyPatternLinkForm(FlaskForm):
    from_stop = SelectField('From Stop', choices=[], validators=[DataRequired()])
    to_stop = SelectField('To Stop', choices=[], validators=[DataRequired()])
    run_time = StringField('Run Time (minutes)', validators=[DataRequired()])
    
class JourneyForm(FlaskForm):
    journey_code = StringField('Journey Code', validators=[DataRequired(), Length(max=20)])
    departure_time = TimeField('Departure Time', format='%H:%M', validators=[DataRequired()])
    days_of_week = SelectField('Days of Week', choices=[
        ('monday_to_friday', 'Monday to Friday'),
        ('monday_to_saturday', 'Monday to Saturday'),
        ('all_week', 'All Week'),
        ('weekends', 'Weekends Only')
    ], validators=[DataRequired()])
    is_frequent_service = BooleanField('Frequent Service')
    frequency_minutes = IntegerField('Frequency (minutes)', validators=[Optional()])
    submit = SubmitField('Save and continue')
