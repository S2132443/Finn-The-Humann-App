"""Transaction routes."""

import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint('transactions', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """List all transactions."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{get_api_url()}/api/v1/transactions")
            transactions = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        transactions = []
    
    return render_template('transactions/index.html', transactions=transactions)


@bp.route('/add', methods=['GET', 'POST'])
def add():
    """Add new transaction."""
    if request.method == 'POST':
        try:
            data = {
                'account_id': request.form['account_id'],
                'transaction_type': request.form['transaction_type'],
                'amount': float(request.form['amount']),
                'currency': request.form.get('currency', 'MYR'),
                'transaction_date': request.form['transaction_date'],
                'description': request.form.get('description') or None,
                'asset_class_id': request.form.get('asset_class_id') or None
            }
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{get_api_url()}/api/v1/transactions", json=data)
                
                if resp.status_code == 201:
                    flash('Transaction recorded successfully', 'success')
                    return redirect(url_for('transactions.index'))
                else:
                    flash(f'Error recording transaction: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
    
    # Get accounts and asset classes for form
    try:
        with httpx.Client(timeout=10.0) as client:
            accounts_resp = client.get(f"{get_api_url()}/api/v1/accounts")
            accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
            classes_resp = client.get(f"{get_api_url()}/api/v1/assets/classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
    except:
        accounts = []
        asset_classes = []

    return render_template(
        'transactions/form.html',
        transaction=None,
        accounts=accounts,
        asset_classes=asset_classes
    )


@bp.route('/<transaction_id>/delete', methods=['POST'])
def delete(transaction_id):
    """Delete transaction."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.delete(f"{get_api_url()}/api/v1/transactions/{transaction_id}")
            
            if resp.status_code == 204:
                flash('Transaction deleted successfully', 'success')
            else:
                flash(f'Error deleting transaction: {resp.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('transactions.index'))
