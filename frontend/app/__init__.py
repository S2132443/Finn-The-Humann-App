"""Flask application factory."""

import os
from flask import Flask


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['API_BASE_URL'] = os.environ.get('API_BASE_URL', 'http://backend:8000')
    
    # Register blueprints
    from app.routes import dashboard, accounts, assets, transactions, income, settings
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(accounts.bp, url_prefix='/accounts')
    app.register_blueprint(assets.bp, url_prefix='/assets')
    app.register_blueprint(transactions.bp, url_prefix='/transactions')
    app.register_blueprint(income.bp, url_prefix='/income')
    app.register_blueprint(settings.bp, url_prefix='/settings')
    
    # Context processor for API URL
    @app.context_processor
    def inject_api_url():
        return {'api_base_url': app.config['API_BASE_URL']}
    
    return app


# Create the application instance
app = create_app()
