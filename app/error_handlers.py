from flask import jsonify, render_template, request
import logging

def register_error_handlers(app):
    """Register error handlers for the Flask application"""

    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Bad request'}), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'success': False, 'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        if request.is_json:
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

def setup_logging(app):
    """Setup logging configuration"""
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )