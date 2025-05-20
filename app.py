from app import create_app
from flask import session, request, make_response
import uuid

app = create_app()

@app.before_request
def before_request():
    # Ensure each user has a session ID for storing their data
    if 'bods_session' not in request.cookies:
        session_id = str(uuid.uuid4())
        # Will set the cookie on the response
        app.bods_session_to_set = session_id

@app.after_request
def after_request(response):
    # Set the session cookie if needed
    if hasattr(app, 'bods_session_to_set'):
        response.set_cookie('bods_session', app.bods_session_to_set)
        delattr(app, 'bods_session_to_set')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5002)
