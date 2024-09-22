from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request'}), 400

