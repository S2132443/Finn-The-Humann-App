"""Account routes."""

import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint('accounts', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """List all accounts."""
    try:
        with httpx.Client(timeout=10.0) as client:
            # Get accounts
            accounts_resp = client.get(f"{get_api_url()}/api/v1/accounts")
            accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
            
            # Get account types
            types_resp = client.get(f"{get_api_url()}/api/v1/accounts/types")
            account_types = types_resp.json() if types_resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        accounts = []
        account_types = []
    
    return render_template('accounts/index.html', accounts=accounts, account_types=account_types)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new account."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'account_type_id': request.form.get('account_type_id') or None,
                'institution': request.form.get('institution') or None,
                'currency': request.form.get('currency', 'MYR'),
                'is_liability': request.form.get('is_liability') == 'on',
                'description': request.form.get('description') or None
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{get_api_url()}/api/v1/accounts", json=data)
                
                if resp.status_code == 201:
                    flash('Account created successfully', 'success')
                    return redirect(url_for('accounts.index'))
                else:
                    flash(f'Error creating account: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get account types and currencies for form
    try:
        with httpx.Client(timeout=10.0) as client:
            types_resp = client.get(f"{get_api_url()}/api/v1/accounts/types")
            account_types = types_resp.json() if types_resp.status_code == 200 else []
            
            currencies_resp = client.get(f"{get_api_url()}/api/v1/settings/currencies")
            currencies = currencies_resp.json() if currencies_resp.status_code == 200 else []
    except:
        account_types = []
        currencies = []
    
    return render_template('accounts/form.html', account=None, account_types=account_types, currencies=currencies)


@bp.route('/<account_id>')
def view(account_id):
    """View account details."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{get_api_url()}/api/v1/accounts/{account_id}")
            if resp.status_code == 200:
                account = resp.json()
            else:
                flash('Account not found', 'danger')
                return redirect(url_for('accounts.index'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('accounts.index'))
    
    return render_template('accounts/view.html', account=account)


@bp.route('/<account_id>/edit', methods=['GET', 'POST'])
def edit(account_id):
    """Edit account."""
    if request.method == 'POST':
        try:
            data = {
                'name': request.form['name'],
                'account_type_id': request.form.get('account_type_id') or None,
                'institution': request.form.get('institution') or None,
                'currency': request.form.get('currency', 'MYR'),
                'is_liability': request.form.get('is_liability') == 'on',
                'description': request.form.get('description') or None
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.put(f"{get_api_url()}/api/v1/accounts/{account_id}", json=data)
                
                if resp.status_code == 200:
                    flash('Account updated successfully', 'success')
                    return redirect(url_for('accounts.view', account_id=account_id))
                else:
                    flash(f'Error updating account: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get account data
    try:
        with httpx.Client(timeout=10.0) as client:
            account_resp = client.get(f"{get_api_url()}/api/v1/accounts/{account_id}")
            account = account_resp.json() if account_resp.status_code == 200 else None
            
            types_resp = client.get(f"{get_api_url()}/api/v1/accounts/types")
            account_types = types_resp.json() if types_resp.status_code == 200 else []
            
            currencies_resp = client.get(f"{get_api_url()}/api/v1/settings/currencies")
            currencies = currencies_resp.json() if currencies_resp.status_code == 200 else []
    except:
        account = None
        account_types = []
        currencies = []
    
    if not account:
        flash('Account not found', 'danger')
        return redirect(url_for('accounts.index'))
    
    return render_template('accounts/form.html', account=account, account_types=account_types, currencies=currencies)


@bp.route('/<account_id>/delete', methods=['POST'])
def delete(account_id):
    """Delete account."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(f"{get_api_url()}/api/v1/accounts/{account_id}")
            
            if resp.status_code == 204:
                flash('Account deleted successfully', 'success')
            else:
                flash(f'Error deleting account: {resp.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('accounts.index'))
