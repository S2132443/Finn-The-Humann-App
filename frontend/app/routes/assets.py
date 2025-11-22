"""Asset routes."""

import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint('assets', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """List all assets."""
    try:
        with httpx.Client(timeout=10.0) as client:
            assets_resp = client.get(f"{get_api_url()}/api/v1/assets")
            assets = assets_resp.json() if assets_resp.status_code == 200 else []
            
            classes_resp = client.get(f"{get_api_url()}/api/v1/assets/classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching assets: {e}")
        assets = []
        asset_classes = []
    
    return render_template('assets/index.html', assets=assets, asset_classes=asset_classes)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new asset."""
    if request.method == 'POST':
        try:
            data = {
                'account_id': request.form['account_id'],
                'asset_class_id': request.form.get('asset_class_id') or None,
                'name': request.form['name'],
                'symbol': request.form.get('symbol') or None,
                'quantity': float(request.form.get('quantity', 0)),
                'current_value': float(request.form.get('current_value', 0)),
                'currency': request.form.get('currency', 'MYR'),
                'cost_basis': float(request.form.get('cost_basis', 0)) if request.form.get('cost_basis') else None,
                'notes': request.form.get('notes') or None
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{get_api_url()}/api/v1/assets", json=data)
                
                if resp.status_code == 201:
                    flash('Asset created successfully', 'success')
                    return redirect(url_for('assets.index'))
                else:
                    flash(f'Error creating asset: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get form data
    try:
        with httpx.Client(timeout=10.0) as client:
            accounts_resp = client.get(f"{get_api_url()}/api/v1/accounts")
            accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
            
            classes_resp = client.get(f"{get_api_url()}/api/v1/assets/classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
            
            currencies_resp = client.get(f"{get_api_url()}/api/v1/settings/currencies")
            currencies = currencies_resp.json() if currencies_resp.status_code == 200 else []
    except:
        accounts = []
        asset_classes = []
        currencies = []
    
    return render_template('assets/form.html', asset=None, accounts=accounts, 
                         asset_classes=asset_classes, currencies=currencies)


@bp.route('/<asset_id>/edit', methods=['GET', 'POST'])
def edit(asset_id):
    """Edit asset."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'quantity': float(request.form.get('quantity', 0)),
                'current_value': float(request.form.get('current_value', 0)),
                'currency': request.form.get('currency', 'MYR'),
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.put(f"{get_api_url()}/api/v1/assets/{asset_id}", json=data)
                
                if resp.status_code == 200:
                    flash('Asset updated successfully', 'success')
                    return redirect(url_for('assets.index'))
                else:
                    flash(f'Error updating asset: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get asset data
    try:
        with httpx.Client(timeout=10.0) as client:
            asset_resp = client.get(f"{get_api_url()}/api/v1/assets/{asset_id}")
            asset = asset_resp.json() if asset_resp.status_code == 200 else None
            
            accounts_resp = client.get(f"{get_api_url()}/api/v1/accounts")
            accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
            
            classes_resp = client.get(f"{get_api_url()}/api/v1/assets/classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
            
            currencies_resp = client.get(f"{get_api_url()}/api/v1/settings/currencies")
            currencies = currencies_resp.json() if currencies_resp.status_code == 200 else []
    except:
        asset = None
        accounts = []
        asset_classes = []
        currencies = []
    
    if not asset:
        flash('Asset not found', 'danger')
        return redirect(url_for('assets.index'))
    
    return render_template('assets/form.html', asset=asset, accounts=accounts,
                         asset_classes=asset_classes, currencies=currencies)


@bp.route('/<asset_id>/delete', methods=['POST'])
def delete(asset_id):
    """Delete asset."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(f"{get_api_url()}/api/v1/assets/{asset_id}")
            
            if resp.status_code == 204:
                flash('Asset deleted successfully', 'success')
            else:
                flash(f'Error deleting asset: {resp.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('assets.index'))
