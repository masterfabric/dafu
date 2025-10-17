"""
DAFU - Data Analytics Functional Utilities
CLI Client for API Interaction
===============================
Python client for interacting with DAFU API

Author: MasterFabric
License: AGPL-3.0
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys


class DAFUClient:
    """Client for interacting with DAFU API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize DAFU client
        
        Args:
            base_url: API base URL
            token: JWT access token
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set headers
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
        if api_key:
            self.session.headers['X-API-Key'] = api_key
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            if response.status_code == 204:
                return {"message": "Success"}
            
            data = response.json()
            
            if response.status_code >= 400:
                error_msg = data.get('detail', 'Unknown error')
                raise Exception(f"API Error ({response.status_code}): {error_msg}")
            
            return data
        except json.JSONDecodeError:
            if response.status_code >= 400:
                raise Exception(f"API Error ({response.status_code}): {response.text}")
            return {"message": "Success"}
    
    # ========================================================================
    # Authentication Methods
    # ========================================================================
    
    def register(self, username: str, email: str, password: str, 
                 full_name: Optional[str] = None, company: Optional[str] = None,
                 phone: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user"""
        data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "company": company,
            "phone": phone
        }
        response = self.session.post(f"{self.base_url}/api/v1/auth/register", json=data)
        return self._handle_response(response)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get JWT token"""
        data = {
            "username": username,
            "password": password
        }
        response = self.session.post(f"{self.base_url}/api/v1/auth/login", json=data)
        result = self._handle_response(response)
        
        # Update token in session
        if 'access_token' in result:
            self.token = result['access_token']
            self.session.headers['Authorization'] = f'Bearer {self.token}'
        
        return result
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        response = self.session.get(f"{self.base_url}/api/v1/auth/me")
        return self._handle_response(response)
    
    def logout(self) -> Dict[str, Any]:
        """Logout current user"""
        response = self.session.post(f"{self.base_url}/api/v1/auth/logout")
        result = self._handle_response(response)
        
        # Clear token
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        
        return result
    
    def change_password(self, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        data = {
            "old_password": old_password,
            "new_password": new_password
        }
        response = self.session.post(f"{self.base_url}/api/v1/auth/change-password", json=data)
        return self._handle_response(response)
    
    def generate_api_key(self) -> Dict[str, Any]:
        """Generate API key"""
        response = self.session.post(f"{self.base_url}/api/v1/auth/api-key")
        return self._handle_response(response)
    
    # ========================================================================
    # Log Methods
    # ========================================================================
    
    def create_log(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create a log entry"""
        data = {
            "level": level,
            "message": message,
            **kwargs
        }
        response = self.session.post(f"{self.base_url}/api/v1/logs/", json=data)
        return self._handle_response(response)
    
    def get_logs(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """Get logs with filtering"""
        params = {"skip": skip, "limit": limit, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/logs/", params=params)
        return self._handle_response(response)
    
    def get_my_logs(self, skip: int = 0, limit: int = 100, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current user's logs"""
        params = {"skip": skip, "limit": limit}
        if level:
            params['level'] = level
        response = self.session.get(f"{self.base_url}/api/v1/logs/my-logs", params=params)
        return self._handle_response(response)
    
    def get_log_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get log statistics"""
        params = {"hours": hours}
        response = self.session.get(f"{self.base_url}/api/v1/logs/stats", params=params)
        return self._handle_response(response)
    
    # ========================================================================
    # Report Methods
    # ========================================================================
    
    def create_report(self, name: str, report_type: str, 
                      description: Optional[str] = None,
                      config: Optional[Dict] = None,
                      filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new report"""
        data = {
            "name": name,
            "description": description,
            "report_type": report_type,
            "config": config or {},
            "filters": filters or {}
        }
        response = self.session.post(f"{self.base_url}/api/v1/reports/", json=data)
        return self._handle_response(response)
    
    def get_reports(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """Get user's reports"""
        params = {"skip": skip, "limit": limit, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/reports/", params=params)
        return self._handle_response(response)
    
    def get_all_reports(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """Get all reports (analyst/admin only)"""
        params = {"skip": skip, "limit": limit, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/reports/all", params=params)
        return self._handle_response(response)
    
    def get_report(self, report_id: int) -> Dict[str, Any]:
        """Get report by ID"""
        response = self.session.get(f"{self.base_url}/api/v1/reports/{report_id}")
        return self._handle_response(response)
    
    def update_report(self, report_id: int, **updates) -> Dict[str, Any]:
        """Update report"""
        response = self.session.put(f"{self.base_url}/api/v1/reports/{report_id}", json=updates)
        return self._handle_response(response)
    
    def delete_report(self, report_id: int) -> Dict[str, Any]:
        """Delete report"""
        response = self.session.delete(f"{self.base_url}/api/v1/reports/{report_id}")
        return self._handle_response(response)
    
    def retry_report(self, report_id: int) -> Dict[str, Any]:
        """Retry failed report"""
        response = self.session.post(f"{self.base_url}/api/v1/reports/{report_id}/retry")
        return self._handle_response(response)
    
    def get_report_stats(self) -> Dict[str, Any]:
        """Get report statistics"""
        response = self.session.get(f"{self.base_url}/api/v1/reports/stats")
        return self._handle_response(response)
    
    # ========================================================================
    # Product Methods
    # ========================================================================
    
    def create_product(self, sku: str, name: str, price: float, **kwargs) -> Dict[str, Any]:
        """Create a new product"""
        data = {
            "sku": sku,
            "name": name,
            "price": price,
            **kwargs
        }
        response = self.session.post(f"{self.base_url}/api/v1/products/", json=data)
        return self._handle_response(response)
    
    def get_products(self, skip: int = 0, limit: int = 100, **filters) -> List[Dict[str, Any]]:
        """Get products"""
        params = {"skip": skip, "limit": limit, **filters}
        response = self.session.get(f"{self.base_url}/api/v1/products/", params=params)
        return self._handle_response(response)
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get product by ID"""
        response = self.session.get(f"{self.base_url}/api/v1/products/{product_id}")
        return self._handle_response(response)
    
    def get_product_by_sku(self, sku: str) -> Dict[str, Any]:
        """Get product by SKU"""
        response = self.session.get(f"{self.base_url}/api/v1/products/sku/{sku}")
        return self._handle_response(response)
    
    def update_product(self, product_id: int, **updates) -> Dict[str, Any]:
        """Update product"""
        response = self.session.put(f"{self.base_url}/api/v1/products/{product_id}", json=updates)
        return self._handle_response(response)
    
    def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete product"""
        response = self.session.delete(f"{self.base_url}/api/v1/products/{product_id}")
        return self._handle_response(response)
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Get product statistics"""
        response = self.session.get(f"{self.base_url}/api/v1/products/stats")
        return self._handle_response(response)
    
    def get_high_risk_products(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get high-risk products"""
        params = {"skip": skip, "limit": limit}
        response = self.session.get(f"{self.base_url}/api/v1/products/high-risk", params=params)
        return self._handle_response(response)
    
    def get_low_stock_products(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get low stock products"""
        params = {"skip": skip, "limit": limit}
        response = self.session.get(f"{self.base_url}/api/v1/products/low-stock", params=params)
        return self._handle_response(response)
    
    def update_product_fraud_risk(self, product_id: int, fraud_risk_score: float, 
                                   high_risk: bool, **kwargs) -> Dict[str, Any]:
        """Update product fraud risk"""
        data = {
            "fraud_risk_score": fraud_risk_score,
            "high_risk": high_risk,
            **kwargs
        }
        response = self.session.put(
            f"{self.base_url}/api/v1/products/{product_id}/fraud-risk",
            json=data
        )
        return self._handle_response(response)
    
    def update_stock(self, product_id: int, quantity: int) -> Dict[str, Any]:
        """Update product stock"""
        params = {"quantity": quantity}
        response = self.session.post(
            f"{self.base_url}/api/v1/products/{product_id}/stock",
            params=params
        )
        return self._handle_response(response)
    
    # ========================================================================
    # Health Check
    # ========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        return self._handle_response(response)


class SessionManager:
    """Manage user sessions and tokens"""
    
    def __init__(self, session_file: str = ".dafu_session"):
        """Initialize session manager"""
        self.session_file = os.path.expanduser(f"~/{session_file}")
    
    def save_session(self, token: str, username: str, expires_in: int):
        """Save session to file"""
        session_data = {
            "token": token,
            "username": username,
            "expires_at": datetime.now().timestamp() + expires_in,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Set file permissions to 600 (read/write for owner only)
        os.chmod(self.session_file, 0o600)
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load session from file"""
        if not os.path.exists(self.session_file):
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if token is expired
            if datetime.now().timestamp() > session_data.get('expires_at', 0):
                self.clear_session()
                return None
            
            return session_data
        except Exception:
            return None
    
    def clear_session(self):
        """Clear session file"""
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
    
    def is_logged_in(self) -> bool:
        """Check if user is logged in"""
        return self.load_session() is not None


def get_client(base_url: str = "http://localhost:8000") -> DAFUClient:
    """
    Get authenticated DAFU client
    
    Loads session if available, otherwise returns unauthenticated client
    """
    session_manager = SessionManager()
    session = session_manager.load_session()
    
    if session:
        return DAFUClient(base_url=base_url, token=session['token'])
    else:
        return DAFUClient(base_url=base_url)


if __name__ == "__main__":
    # Example usage
    client = DAFUClient()
    
    try:
        # Health check
        health = client.health_check()
        print("API Health:", health)
    except Exception as e:
        print(f"Error: {e}")

