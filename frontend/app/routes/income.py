"""Income routes."""

import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint('income', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """List all income records."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{get_api_url()}/api/v1/income")
            income_records = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching income: {e}")
        income_records = []
    
    return render_template('income/index.html', income_records=income_records)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new income record."""
    if request.method == 'POST':
        try:
            data = {
                'account_id': request.form['account_id'],
                'asset_id': request.form.get('asset_id') or None,
                'income_type': request.form['income_type'],
                'amount': float(request.form['amount']),
                'currency': request.form.get('currency', 'MYR'),
                'income_date': request.form['income_date'],
                'description': request.form.get('description') or None,
                'is_reinvested': request.form.get('is_reinvested') == 'on'
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{get_api_url()}/api/v1/income", json=data)
                
                if resp.status_code == 201:
                    flash('Income recorded successfully', 'success')
                    return redirect(url_for('income.index'))
                else:
                    flash(f'Error recording income: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get form data
    try:
        with httpx.Client(timeout=10.0) as client:
            accounts_resp = client.get(f"{get_api_url()}/api/v1/accounts")
            accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
            
            assets_resp = client.get(f"{get_api_url()}/api/v1/assets")
            assets = assets_resp.json() if assets_resp.status_code == 200 else []
    except:
        accounts = []
        assets = []
    
    return render_template('income/form.html', income=None, accounts=accounts, assets=assets)


@bp.route('/<income_id>/delete', methods=['POST'])
def delete(income_id):
    """Delete income record."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(f"{get_api_url()}/api/v1/income/{income_id}")
            
            if resp.status_code == 204:
                flash('Income record deleted successfully', 'success')
            else:
                flash(f'Error deleting income: {resp.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('income.index'))
