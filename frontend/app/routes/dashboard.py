"""Dashboard routes."""

import httpx
from flask import Blueprint, render_template, current_app

bp = Blueprint('dashboard', __name__)


def get_api_url():
    """Get the API base URL."""
    return current_app.config['API_BASE_URL']


@bp.route('/')
def index():
    """Main dashboard view."""
    try:
        # Fetch data from API
        with httpx.Client(timeout=10.0) as client:
            # Get net worth
            networth_resp = client.get(f"{get_api_url()}/api/v1/networth")
            networth = networth_resp.json() if networth_resp.status_code == 200 else None
            
            # Get allocation
            allocation_resp = client.get(f"{get_api_url()}/api/v1/allocation")
            allocation = allocation_resp.json() if allocation_resp.status_code == 200 else None
            
            # Get net worth history
            history_resp = client.get(f"{get_api_url()}/api/v1/networth/history?months=12")
            history = history_resp.json() if history_resp.status_code == 200 else None
            
            # Get income summary
            income_resp = client.get(f"{get_api_url()}/api/v1/income/summary")
            income_summary = income_resp.json() if income_resp.status_code == 200 else None
            
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        networth = None
        allocation = None
        history = None
        income_summary = None
    
    return render_template(
        'dashboard.html',
        networth=networth,
        allocation=allocation,
        history=history,
        income_summary=income_summary
    )
