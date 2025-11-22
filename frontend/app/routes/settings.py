"""Settings routes."""

import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

bp = Blueprint('settings', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """Settings overview."""
    try:
        with httpx.Client(timeout=10.0) as client:
            # Get asset classes
            classes_resp = client.get(f"{get_api_url()}/api/v1/settings/asset-classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
            
            # Get currencies
            currencies_resp = client.get(f"{get_api_url()}/api/v1/settings/currencies")
            currencies = currencies_resp.json() if currencies_resp.status_code == 200 else []
            
            # Get strategic allocation
            allocation_resp = client.get(f"{get_api_url()}/api/v1/settings/strategic-allocation")
            allocations = allocation_resp.json() if allocation_resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching settings: {e}")
        asset_classes = []
        currencies = []
        allocations = []
    
    return render_template('settings/index.html', 
                         asset_classes=asset_classes, 
                         currencies=currencies,
                         allocations=allocations)


@bp.route('/allocation', methods=['GET', 'POST'])
def allocation():
    """Manage strategic asset allocation."""
    if request.method == 'POST':
        try:
            # Get form data
            allocations = []
            for key in request.form:
                if key.startswith('allocation_'):
                    class_id = key.replace('allocation_', '')
                    percentage = float(request.form[key])
                    allocations.append({
                        'asset_class_id': class_id,
                        'target_percentage': percentage,
                        'effective_date': request.form['effective_date']
                    })
            
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{get_api_url()}/api/v1/settings/strategic-allocation/bulk",
                    json=allocations
                )
                
                if resp.status_code == 200:
                    flash('Strategic allocation updated successfully', 'success')
                else:
                    flash(f'Error updating allocation: {resp.text}', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('settings.index'))
    
    # Get asset classes for form
    try:
        with httpx.Client(timeout=10.0) as client:
            classes_resp = client.get(f"{get_api_url()}/api/v1/settings/asset-classes")
            asset_classes = classes_resp.json() if classes_resp.status_code == 200 else []
            
            allocation_resp = client.get(f"{get_api_url()}/api/v1/settings/strategic-allocation")
            allocations = allocation_resp.json() if allocation_resp.status_code == 200 else []
    except:
        asset_classes = []
        allocations = []
    
    return render_template('settings/allocation.html', 
                         asset_classes=asset_classes, 
                         allocations=allocations)


@bp.route('/snapshots')
def snapshots():
    """View and manage snapshots."""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{get_api_url()}/api/v1/snapshots")
            snapshots = resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"Error fetching snapshots: {e}")
        snapshots = []
    
    return render_template('settings/snapshots.html', snapshots=snapshots)


@bp.route('/snapshots/create', methods=['POST'])
def create_snapshot():
    """Create a new snapshot."""
    try:
        data = {
            'snapshot_date': request.form['snapshot_date']
        }
        
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(f"{get_api_url()}/api/v1/snapshots", json=data)
            
            if resp.status_code == 201:
                flash('Snapshot created successfully', 'success')
            else:
                flash(f'Error creating snapshot: {resp.text}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('settings.snapshots'))
