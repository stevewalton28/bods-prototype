# BODS Data Submission Service

A GOV.UK-styled web application that helps small bus operators efficiently capture, validate, and generate TransXChange XML files for submission to the Bus Open Data Service (BODS).

## Overview

The Bus Open Data Service (BODS) requires all bus operators in the UK to submit their timetables, fares, and location data in specific formats. Small operators often find it challenging to create valid XML files that comply with the TransXChange schema.

This application simplifies the process by:

1. Providing a user-friendly form interface following GOV.UK Design System patterns
2. Guiding operators through the data entry process step-by-step
3. Validating input data against the TransXChange schema requirements
4. Generating compliant XML files that can be submitted to BODS

## Features

- Comprehensive data collection for operators, services, routes, stops, and journeys
- Built using the GOV.UK Design System for a familiar, accessible user interface
- Step-by-step wizard approach to data collection
- XML validation against the TransXChange 2.4 schema
- Demo-friendly implementation for showcasing to customers

## Technical Implementation

- Built with Python (Flask) for the backend
- Uses the GOV.UK Design System for frontend styling and components
- XML schema validation using `xmlschema` library
- Form handling with WTForms and Flask-WTF

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bods
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```
   
5. Access the application in your web browser at:
   ```
   http://localhost:5000
   ```

## Project Structure

```
bods/
├── app/                   # Application package
│   ├── main/              # Main blueprint
│   │   ├── __init__.py
│   │   ├── forms.py       # Form definitions
│   │   └── routes.py      # Route handlers
│   ├── models/            # Data models
│   ├── static/            # Static files (CSS, JS)
│   ├── templates/         # HTML templates
│   ├── validators/        # Custom validators
│   └── __init__.py        # App factory
├── schema/                # TransXChange XML schemas
├── output/                # Generated XML files
├── venv/                  # Virtual environment
├── .gitignore             # Git ignore file
├── app.py                 # Application entry point
├── config.py              # Configuration
└── requirements.txt       # Python dependencies
```

## Usage

1. Start at the home page and follow the step-by-step process
2. Enter operator details including licence information
3. Provide service information such as route IDs and line numbers
4. Add bus stops along the route
5. Enter journey patterns and timetable information
6. Review the entered information
7. Generate and download the TransXChange XML file
8. Submit the downloaded file to the BODS service

## Development

### Requirements

- Python 3.7+
- Flask 2.2+
- XML schema validation libraries

### Testing

Run the test suite with:

```
pytest
```

## License

This project is licensed under the terms of the MIT license.

## GOV.UK Design System

This application follows the [GOV.UK Design System](https://design-system.service.gov.uk/) guidelines and patterns to ensure a consistent, accessible user experience that will be familiar to users of UK government services.
