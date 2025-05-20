from flask import render_template, redirect, url_for, flash, request, current_app, send_from_directory, session
from app.main import bp
from app.main.forms import OperatorForm, ServiceForm, RouteForm, JourneyForm, StopForm
import os
import xml.etree.ElementTree as ET
from app.validators.xml_validator import validate_xml
from datetime import datetime
import uuid
import requests
import json

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/start')
def start():
    return render_template('start.html', title='Start')

@bp.route('/operator', methods=['GET', 'POST'])
def operator():
    form = OperatorForm()
    if form.validate_on_submit():
        # Save operator data to session
        session['operator_code'] = form.operator_code.data
        session['operator_short_name'] = form.operator_short_name.data
        session['operator_name_on_licence'] = form.operator_name_on_licence.data
        session['trading_name'] = form.trading_name.data
        session['licence_number'] = form.licence_number.data
        session['licence_classification'] = form.licence_classification.data
        session['contact_person'] = form.contact_person.data
        session['telephone'] = form.telephone.data
        session['email'] = form.email.data
        session['website'] = form.website.data
        session['address_line1'] = form.address_line1.data
        session['address_line2'] = form.address_line2.data
        session['address_line3'] = form.address_line3.data
        session['town'] = form.town.data
        session['postcode'] = form.postcode.data
        
        session.modified = True
        flash('Operator information saved successfully')
        return redirect(url_for('main.service'))
    return render_template('operator.html', title='Operator Details', form=form)

@bp.route('/service', methods=['GET', 'POST'])
def service():
    form = ServiceForm()
    if form.validate_on_submit():
        # Save service data to session
        session['service_code'] = form.service_code.data
        session['line_name'] = form.line_name.data
        session['start_date'] = form.start_date.data.strftime('%Y-%m-%d') if form.start_date.data else None
        session['description'] = form.description.data
        session['origin'] = form.origin.data
        session['destination'] = form.destination.data
        session['wheelchair_accessible'] = form.wheelchair_accessible.data
        
        session.modified = True
        flash('Service information saved successfully')
        return redirect(url_for('main.route'))
    return render_template('service.html', title='Service Details', form=form)

@bp.route('/route', methods=['GET', 'POST'])
def route():
    form = RouteForm()
    if form.validate_on_submit():
        # Save route data to session
        session['route_id'] = form.route_id.data
        session['route_description'] = form.description.data
        session['direction'] = form.direction.data
        
        session.modified = True
        flash('Route information saved successfully')
        return redirect(url_for('main.stops'))
    return render_template('route.html', title='Route Details', form=form)

@bp.route('/stops', methods=['GET', 'POST'])
@bp.route('/stops/<mode>', methods=['GET', 'POST'])
@bp.route('/stops/<mode>/<int:stop_id>', methods=['GET', 'POST'])
def stops(mode='list', stop_id=None):
    # Initialize or get existing stops from session
    if 'stops' not in session:
        session['stops'] = []
    
    if mode == 'add':
        # Add new stop
        form = StopForm()
        if form.validate_on_submit():
            stop_data = {
                'atco_code': form.atco_code.data,
                'naptan_code': form.naptan_code.data,
                'common_name': form.common_name.data,
                'indicator': form.indicator.data,
                'locality': form.locality.data,
                'longitude': form.longitude.data,
                'latitude': form.latitude.data,
                'travel_time_to_next': None
            }
            
            # Add the new stop
            session['stops'].append(stop_data)
            
            # Update travel times for all stops
            session['stops'] = update_travel_times(session['stops'])
            session.modified = True
            flash('Stop added successfully')
            return redirect(url_for('main.stops', mode='list'))
        return render_template('stops.html', title='Add Stop', form=form, mode=mode, stop_id=stop_id)
    
    elif mode == 'edit' and stop_id is not None:
        # Edit existing stop
        if stop_id < 0 or stop_id >= len(session['stops']):
            flash('Invalid stop ID', 'error')
            return redirect(url_for('main.stops', mode='list'))
        
        stop_data = session['stops'][stop_id]
        form = StopForm()
        
        if request.method == 'GET':
            # Pre-populate form with existing data
            form.atco_code.data = stop_data.get('atco_code', '')
            form.naptan_code.data = stop_data.get('naptan_code', '')
            form.common_name.data = stop_data.get('common_name', '')
            form.indicator.data = stop_data.get('indicator', '')
            form.locality.data = stop_data.get('locality', '')
            form.longitude.data = stop_data.get('longitude', '')
            form.latitude.data = stop_data.get('latitude', '')
        
        if form.validate_on_submit():
            # Update stop data
            stop_data = {
                'atco_code': form.atco_code.data,
                'naptan_code': form.naptan_code.data,
                'common_name': form.common_name.data,
                'indicator': form.indicator.data,
                'locality': form.locality.data,
                'longitude': form.longitude.data,
                'latitude': form.latitude.data,
                'travel_time_to_next': session['stops'][stop_id].get('travel_time_to_next') 
            }
            
            # Update the stop
            session['stops'][stop_id] = stop_data
            
            # Recalculate travel times for all stops
            session['stops'] = update_travel_times(session['stops'])
            session.modified = True
            flash('Stop updated successfully')
            return redirect(url_for('main.stops', mode='list'))
        return render_template('stops.html', title='Edit Stop', form=form, mode=mode, stop_id=stop_id)
    
    elif mode == 'remove' and stop_id is not None:
        # Remove stop
        if stop_id < 0 or stop_id >= len(session['stops']):
            flash('Invalid stop ID', 'error')
            return redirect(url_for('main.stops', mode='list'))
        
        stop = session['stops'][stop_id]
        
        if request.method == 'POST':
            # Process removal confirmation
            confirm_remove = request.form.get('confirm_remove')
            if confirm_remove == 'yes':
                session['stops'].pop(stop_id)
                session.modified = True
                flash('Stop removed successfully')
            return redirect(url_for('main.stops', mode='list'))
        
        form = StopForm()  # Create an empty form for the template
        return render_template('stops.html', title='Remove Stop', form=form, mode=mode, stop_id=stop_id, stop=stop)
    
    else:  # mode == 'list'
        # Display list of stops
        form = StopForm()  # Create an empty form for the template
        return render_template('stops.html', title='Stop Points', form=form, mode='list', stops=session.get('stops', []))


@bp.route('/journey', methods=['GET', 'POST'])
def journey():
    form = JourneyForm()
    if form.validate_on_submit():
        # Save journey data to session
        session['journey_code'] = form.journey_code.data
        session['departure_time'] = form.departure_time.data.strftime('%H:%M') if form.departure_time.data else None
        session['days_of_week'] = form.days_of_week.data
        session['is_frequent_service'] = form.is_frequent_service.data
        session['frequency_minutes'] = form.frequency_minutes.data
        
        session.modified = True
        flash('Journey information saved successfully')
        return redirect(url_for('main.review'))
    return render_template('journey.html', title='Journey Details', form=form)

@bp.route('/review')
def review():
    # Retrieve all the saved data and display for review
    return render_template('review.html', title='Review Submission')

@bp.route('/generate', methods=['POST'])
def generate():
    # Generate XML file based on the data provided
    try:
        xml_file = generate_transxchange_xml()
        filename = f"transxchange_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
        filepath = os.path.join(current_app.config['OUTPUT_DIR'], filename)
        
        # Save the XML file
        with open(filepath, 'wb') as f:
            f.write(xml_file)
            
        flash('XML generated successfully!')
        return redirect(url_for('main.download', filename=filename))
    except Exception as e:
        flash(f'Error generating XML: {str(e)}', 'error')
        return redirect(url_for('main.review'))

@bp.route('/download/<filename>')
def download(filename):
    return render_template('download.html', title='Download XML', filename=filename)

@bp.route('/get-file/<filename>')
def get_file(filename):
    return send_from_directory(
        current_app.config['OUTPUT_DIR'], 
        filename, 
        as_attachment=True
    )

def calculate_travel_time(start_coords, end_coords):
    """Calculate travel time between two points using OpenRouteService API.
    
    Args:
        start_coords: tuple of (longitude, latitude) for start point
        end_coords: tuple of (longitude, latitude) for end point
        
    Returns:
        Travel time in minutes or None if calculation fails
    """
    api_key = current_app.config.get('OPENROUTE_SERVICE_API_KEY')
    if not api_key or not start_coords or not end_coords:
        return None
        
    # Skip calculation if coordinates are invalid
    try:
        start_long, start_lat = float(start_coords[0]), float(start_coords[1])
        end_long, end_lat = float(end_coords[0]), float(end_coords[1])
    except (ValueError, TypeError):
        return None
        
    # OpenRouteService expects [longitude, latitude] format
    coordinates = [[start_long, start_lat], [end_long, end_lat]]
    
    # Prepare request body
    body = {
        "coordinates": coordinates,
        "instructions": False,
        "preference": "recommended",
        "units": "m",
        "geometry": False,  # Don't need geometry, just time
        "profile": "driving-hgv",  # Use HGV profile for buses
        "options": {
            "profile_params": {
                "restrictions": {
                    "height": 4.4,  # Standard UK double-decker height
                    "width": 2.55   # Standard UK bus width
                }
            }
        }
    }
    
    try:
        # Make the API request
        response = requests.post(
            'https://api.openrouteservice.org/v2/directions/driving-hgv/json',
            headers={
                'Accept': 'application/json',
                'Authorization': api_key,
                'Content-Type': 'application/json'
            },
            data=json.dumps(body)
        )
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            # Extract duration in seconds and convert to minutes
            if 'routes' in data and len(data['routes']) > 0:
                duration_seconds = data['routes'][0]['summary']['duration']
                return round(duration_seconds / 60)  # Convert to minutes and round
    except Exception as e:
        # Log the error but continue without travel time
        print(f"Error calculating travel time: {e}")
        
    return None

def update_travel_times(stops):
    """Update travel times for all stops in the list.
    
    Args:
        stops: List of stop dictionaries
        
    Returns:
        Updated list of stops with travel_time_to_next values
    """
    for i in range(len(stops) - 1):
        current_stop = stops[i]
        next_stop = stops[i + 1]
        
        # Skip if either stop is missing coordinates
        if not current_stop.get('longitude') or not current_stop.get('latitude') or \
           not next_stop.get('longitude') or not next_stop.get('latitude'):
            current_stop['travel_time_to_next'] = None
            continue
        
        # Calculate travel time to next stop
        travel_time = calculate_travel_time(
            (current_stop['longitude'], current_stop['latitude']),
            (next_stop['longitude'], next_stop['latitude'])
        )
        
        # Update the stop with travel time
        current_stop['travel_time_to_next'] = travel_time
    
    # Last stop has no next stop
    if stops and len(stops) > 0:
        stops[-1]['travel_time_to_next'] = None
        
    return stops

def generate_transxchange_xml():
    """Generate a TransXChange XML document using the data stored in the session.
    
    Returns:
        bytes: The XML document as a UTF-8 encoded byte string.
    """
    from datetime import datetime, timedelta
    from flask import session
    import uuid
    
    # Generate a unique file identifier
    file_id = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Create root element with namespaces
    root = ET.Element('TransXChange', {
        'xmlns': 'http://www.transxchange.org.uk/',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.transxchange.org.uk/ http://www.transxchange.org.uk/schema/2.4/TransXChange_registration.xsd',
        'CreationDateTime': datetime.now().isoformat(),
        'ModificationDateTime': datetime.now().isoformat(),
        'Modification': 'new',
        'RevisionNumber': '1',
        'FileName': f"transxchange_{file_id}.xml",
        'SchemaVersion': '2.4'
    })
    
    # ============================================================
    # OPERATORS SECTION
    # ============================================================
    operators = ET.SubElement(root, 'Operators')
    operator = ET.SubElement(operators, 'LicensedOperator', {'id': 'O1'})
    
    # Use operator data from session, with fallbacks for required fields
    ET.SubElement(operator, 'NationalOperatorCode').text = session.get('operator_code', 'UNKNOWN')
    ET.SubElement(operator, 'OperatorCode').text = session.get('operator_code', 'UNKNOWN')
    ET.SubElement(operator, 'OperatorShortName').text = session.get('operator_short_name', 'Unknown Operator')
    ET.SubElement(operator, 'OperatorNameOnLicence').text = session.get('operator_name_on_licence', 'Unknown Operator Name')
    ET.SubElement(operator, 'TradingName').text = session.get('trading_name', '')
    
    # Operator contact details
    if session.get('contact_person') or session.get('telephone') or session.get('email'):
        contact_details = ET.SubElement(operator, 'ContactDetails')
        
        if session.get('contact_person'):
            ET.SubElement(contact_details, 'ContactPerson').text = session.get('contact_person')
        
        if session.get('telephone'):
            ET.SubElement(contact_details, 'Phone').text = session.get('telephone')
            
        if session.get('email'):
            ET.SubElement(contact_details, 'Email').text = session.get('email')
            
        if session.get('website'):
            ET.SubElement(contact_details, 'Url').text = session.get('website')
    
    # Operator address
    if session.get('address_line1'):
        address = ET.SubElement(operator, 'CorrespondenceAddress')
        address_line = ET.SubElement(address, 'Line1')
        address_line.text = session.get('address_line1', '')
        
        if session.get('address_line2'):
            address_line = ET.SubElement(address, 'Line2')
            address_line.text = session.get('address_line2')
            
        if session.get('address_line3'):
            address_line = ET.SubElement(address, 'Line3')
            address_line.text = session.get('address_line3')
        
        if session.get('town'):
            ET.SubElement(address, 'Town').text = session.get('town')
            
        if session.get('postcode'):
            ET.SubElement(address, 'PostCode').text = session.get('postcode')
    
    # Operator license info
    if session.get('licence_number'):
        license_info = ET.SubElement(operator, 'LicenceDetails')
        ET.SubElement(license_info, 'LicenceNumber').text = session.get('licence_number')
        ET.SubElement(license_info, 'LicenceClassification').text = session.get('licence_classification', 'standardNational')
    
    # ============================================================
    # SERVICES SECTION
    # ============================================================
    services = ET.SubElement(root, 'Services')
    service = ET.SubElement(services, 'Service')
    
    # Service code and line name
    ET.SubElement(service, 'ServiceCode').text = session.get('service_code', f'SVC{file_id}')
    line_name = ET.SubElement(service, 'Lines')
    line = ET.SubElement(line_name, 'Line', {'id': 'L1'})
    ET.SubElement(line, 'LineName').text = session.get('line_name', 'Unknown Line')
    
    # Service description
    if session.get('description'):
        ET.SubElement(service, 'Description').text = session.get('description')
    
    # Service operating period
    op_period = ET.SubElement(service, 'OperatingPeriod')
    
    # Use start date from session or default to today
    start_date = session.get('start_date')
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            start_date_obj = datetime.now()
    else:
        start_date_obj = datetime.now()
    
    ET.SubElement(op_period, 'StartDate').text = start_date_obj.strftime('%Y-%m-%d')
    
    # Add a default end date (1 year from start)
    end_date_obj = start_date_obj + timedelta(days=365)
    ET.SubElement(op_period, 'EndDate').text = end_date_obj.strftime('%Y-%m-%d')
    
    # Service origin and destination
    if session.get('origin') or session.get('destination'):
        org_dest = ET.SubElement(service, 'OriginDestination')
        if session.get('origin'):
            ET.SubElement(org_dest, 'Origin').text = session.get('origin')
        if session.get('destination'):
            ET.SubElement(org_dest, 'Destination').text = session.get('destination')
    
    # ============================================================
    # STOP POINTS SECTION
    # ============================================================
    stops_data = session.get('stops', [])
    
    if stops_data:
        stop_points = ET.SubElement(root, 'StopPoints')
        
        # Add each stop as a AnnotatedStopPointRef
        for idx, stop in enumerate(stops_data):
            stop_id = f"BS{idx+1:03d}"
            stop_point = ET.SubElement(stop_points, 'StopPoint', {'id': stop_id})
            
            # ATCO and/or NaPTAN code if available
            if stop.get('atco_code'):
                ET.SubElement(stop_point, 'AtcoCode').text = stop.get('atco_code')
            elif stop.get('naptan_code'):
                ET.SubElement(stop_point, 'NaptanCode').text = stop.get('naptan_code')
            else:
                # Generate a placeholder code if neither is available
                ET.SubElement(stop_point, 'AtcoCode').text = f"ATCO{idx+1:04d}"
            
            # Stop name and locality
            common_name = ET.SubElement(stop_point, 'Descriptor')
            ET.SubElement(common_name, 'CommonName').text = stop.get('common_name', f"Stop {idx+1}")
            
            if stop.get('indicator'):
                ET.SubElement(common_name, 'Indicator').text = stop.get('indicator')
                
            if stop.get('locality'):
                ET.SubElement(common_name, 'LocalityName').text = stop.get('locality')
            
            # Location (longitude/latitude)
            if stop.get('longitude') and stop.get('latitude'):
                location = ET.SubElement(stop_point, 'Location')
                ET.SubElement(location, 'Longitude').text = stop.get('longitude')
                ET.SubElement(location, 'Latitude').text = stop.get('latitude')
    
        # ============================================================
        # ROUTES SECTION
        # ============================================================
        routes = ET.SubElement(root, 'Routes')
        route = ET.SubElement(routes, 'Route', {'id': 'R1'})
        
        # Route description
        ET.SubElement(route, 'Description').text = session.get('route_description', 'Unknown Route')
        
        # Route direction
        ET.SubElement(route, 'Direction').text = session.get('direction', 'outbound')
        
        # Route section with ordered stops
        route_section = ET.SubElement(route, 'RouteSection', {'id': 'RS1'})
        
        # Add stops to route section
        for idx in range(len(stops_data)):
            # Use the same IDs as generated in StopPoints section
            from_stop_id = f"BS{idx+1:03d}"
            
            # If not the last stop, create a route link
            if idx < len(stops_data) - 1:
                to_stop_id = f"BS{idx+2:03d}"
                route_link = ET.SubElement(route_section, 'RouteLink', {'id': f"RL{idx+1}_{idx+2}"})
                ET.SubElement(route_link, 'From', {'SequenceNumber': str(idx+1), 'id': from_stop_id})
                ET.SubElement(route_link, 'To', {'SequenceNumber': str(idx+2), 'id': to_stop_id})
                
                # Add estimated running time (based on our calculated travel times)
                if idx < len(stops_data) and stops_data[idx].get('travel_time_to_next') is not None:
                    run_time = stops_data[idx].get('travel_time_to_next')
                    run_time_text = f"PT{run_time}M" if run_time else "PT5M"  # Default 5 minutes if not available
                    ET.SubElement(route_link, 'RunTime').text = run_time_text
                else:
                    # Default run time
                    ET.SubElement(route_link, 'RunTime').text = "PT5M"  # 5 minutes
    
        # ============================================================
        # JOURNEY PATTERNS SECTION
        # ============================================================
        journey_patterns = ET.SubElement(root, 'JourneyPatterns')
        jp = ET.SubElement(journey_patterns, 'JourneyPattern', {'id': 'JP1'})
        
        # Journey pattern sections
        jps = ET.SubElement(jp, 'JourneyPatternSections')
        jp_section = ET.SubElement(jps, 'JourneyPatternSection', {'id': 'JPS1'})
        
        # Add timing links for each pair of stops
        for idx in range(len(stops_data) - 1):
            # Create timing link with run time
            timing_link = ET.SubElement(jp_section, 'JourneyPatternTimingLink', {'id': f"JPTL{idx+1:02d}"})
            
            # Reference to stops
            from_stop_id = f"BS{idx+1:03d}"
            to_stop_id = f"BS{idx+2:03d}"
            
            ET.SubElement(timing_link, 'From', {'SequenceNumber': str(idx+1), 'StopPointRef': from_stop_id, 'Activity': 'pickUp'})
            ET.SubElement(timing_link, 'To', {'SequenceNumber': str(idx+2), 'StopPointRef': to_stop_id, 'Activity': 'setDown'})
            
            # Run time
            if idx < len(stops_data) and stops_data[idx].get('travel_time_to_next') is not None:
                run_time = stops_data[idx].get('travel_time_to_next')
                run_time_text = f"PT{run_time}M" if run_time else "PT5M"  # Default 5 minutes if not available
                ET.SubElement(timing_link, 'RunTime').text = run_time_text
            else:
                # Default run time
                ET.SubElement(timing_link, 'RunTime').text = "PT5M"  # 5 minutes
    
        # ============================================================
        # VEHICLE JOURNEYS SECTION
        # ============================================================
        vehicle_journeys = ET.SubElement(root, 'VehicleJourneys')
        
        # Get journey data
        journey_code = session.get('journey_code', 'J1')
        departure_time = session.get('departure_time', '09:00')
        days_of_week = session.get('days_of_week', 'monday_to_friday')
        is_frequent = session.get('is_frequent_service', False)
        frequency_mins = session.get('frequency_minutes', 60)
        
        # If frequent service, create multiple vehicle journeys
        if is_frequent and frequency_mins and int(frequency_mins) > 0:
            # Number of services (e.g. every hour for 14 hours = 14 services)
            hours_of_operation = 14  # Example: 6am to 8pm
            frequency_mins = int(frequency_mins)
            num_services = (hours_of_operation * 60) // frequency_mins
            
            # Create journeys
            for i in range(num_services):
                if departure_time:
                    try:
                        # Parse original departure time
                        hours, minutes = map(int, departure_time.split(':'))
                        # Add frequency minutes for each journey
                        new_minutes = (minutes + i * frequency_mins) % 60
                        new_hours = hours + (minutes + i * frequency_mins) // 60
                        
                        # Skip if we go beyond 24 hours
                        if new_hours >= 24:
                            continue
                            
                        journey_time = f"{new_hours:02d}:{new_minutes:02d}"
                    except:
                        # Default to original time if parsing fails
                        journey_time = departure_time
                else:
                    # Default time
                    journey_time = '09:00'
                
                # Create vehicle journey
                vj = ET.SubElement(vehicle_journeys, 'VehicleJourney', {'id': f"{journey_code}_{i+1}"})
                ET.SubElement(vj, 'ServiceRef').text = session.get('service_code', f'SVC{file_id}')
                ET.SubElement(vj, 'LineRef').text = 'L1'
                ET.SubElement(vj, 'JourneyPatternRef').text = 'JP1'
                
                # Departure time
                ET.SubElement(vj, 'DepartureTime').text = journey_time
                
                # Operating profile
                add_operating_profile(vj, days_of_week)
        else:
            # Create a single vehicle journey
            vj = ET.SubElement(vehicle_journeys, 'VehicleJourney', {'id': journey_code})
            ET.SubElement(vj, 'ServiceRef').text = session.get('service_code', f'SVC{file_id}')
            ET.SubElement(vj, 'LineRef').text = 'L1'
            ET.SubElement(vj, 'JourneyPatternRef').text = 'JP1'
            
            # Departure time
            ET.SubElement(vj, 'DepartureTime').text = departure_time or '09:00'
            
            # Operating profile
            add_operating_profile(vj, days_of_week)
    
    # Convert to string with pretty print
    from lxml import etree
    xml_str = etree.tostring(
        etree.fromstring(ET.tostring(root)), 
        pretty_print=True, 
        xml_declaration=True, 
        encoding='UTF-8'
    )
    
    # Validate against schema before returning
    # Commented out for now, but can be enabled for production
    # is_valid, errors = validate_xml(xml_str)
    # if not is_valid:
    #     raise ValueError(f"Generated XML is not valid: {errors}")
    
    return xml_str


def add_operating_profile(vehicle_journey, days_of_week):
    """Add operating profile to a vehicle journey based on days of week.
    
    Args:
        vehicle_journey: The XML VehicleJourney element
        days_of_week: String identifier for days of operation
    """
    op_profile = ET.SubElement(vehicle_journey, 'OperatingProfile')
    reg_days = ET.SubElement(op_profile, 'RegularDayType')
    days_operation = ET.SubElement(reg_days, 'DaysOfWeek')
    
    # Set days of operation based on selection
    if days_of_week == 'monday_to_friday':
        ET.SubElement(days_operation, 'MondayToFriday')
    elif days_of_week == 'monday_to_saturday':
        ET.SubElement(days_operation, 'MondayToSaturday')
    elif days_of_week == 'all_week':
        ET.SubElement(days_operation, 'MondayToSunday')
    elif days_of_week == 'weekends':
        ET.SubElement(days_operation, 'Saturday')
        ET.SubElement(days_operation, 'Sunday')
    else:
        # Default to Monday to Friday
        ET.SubElement(days_operation, 'MondayToFriday')
