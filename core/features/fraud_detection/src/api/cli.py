#!/usr/bin/env python3
"""
DAFU - Data Analytics Functional Utilities
CLI Tool for API Interaction
=============================
Interactive command-line interface for DAFU API

Author: MasterFabric
License: AGPL-3.0
"""

import sys
import os
import json
import getpass
from typing import Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .cli_client import DAFUClient, SessionManager, get_client


# ============================================================================
# Colors for Terminal Output
# ============================================================================

class Colors:
    """ANSI color codes"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.NC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.NC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")


def print_title(title: str):
    """Print title"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}\n")


def print_table(headers: list, rows: list):
    """Print formatted table"""
    if not rows:
        print_warning("No data to display")
        return
    
    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(f"{Colors.BOLD}{header_line}{Colors.NC}")
    print("-" * len(header_line))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


# ============================================================================
# CLI Commands
# ============================================================================

class DAFUCLI:
    """DAFU CLI Application"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize CLI"""
        self.base_url = base_url
        self.session_manager = SessionManager()
        self.client = None
        self._load_session()
    
    def _load_session(self):
        """Load existing session"""
        session = self.session_manager.load_session()
        if session:
            self.client = DAFUClient(base_url=self.base_url, token=session['token'])
            print_info(f"Logged in as: {Colors.GREEN}{session['username']}{Colors.NC}")
        else:
            self.client = DAFUClient(base_url=self.base_url)
    
    def require_auth(self):
        """Check if user is authenticated"""
        if not self.session_manager.is_logged_in():
            print_error("You must be logged in to use this command")
            print_info("Use 'dafu auth login' to log in")
            sys.exit(1)
    
    # ========================================================================
    # Authentication Commands
    # ========================================================================
    
    def cmd_auth_register(self, args):
        """Register a new user"""
        print_title("User Registration")
        
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm Password: ")
        
        if password != confirm_password:
            print_error("Passwords do not match")
            return
        
        full_name = input("Full Name (optional): ").strip() or None
        company = input("Company (optional): ").strip() or None
        phone = input("Phone (optional): ").strip() or None
        
        try:
            result = self.client.register(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                company=company,
                phone=phone
            )
            print_success(f"User '{username}' registered successfully!")
            print_info("You can now login with your credentials")
        except Exception as e:
            print_error(f"Registration failed: {e}")
    
    def cmd_auth_login(self, args):
        """Login to DAFU"""
        print_title("User Login")
        
        username = input("Username or Email: ").strip()
        password = getpass.getpass("Password: ")
        
        try:
            result = self.client.login(username, password)
            
            # Save session
            self.session_manager.save_session(
                token=result['access_token'],
                username=username,
                expires_in=result['expires_in']
            )
            
            print_success(f"Logged in as '{username}'")
            print_info(f"Token expires in: {result['expires_in']//3600} hours")
        except Exception as e:
            print_error(f"Login failed: {e}")
    
    def cmd_auth_logout(self, args):
        """Logout from DAFU"""
        self.require_auth()
        
        try:
            self.client.logout()
            self.session_manager.clear_session()
            print_success("Logged out successfully")
        except Exception as e:
            # Clear session anyway
            self.session_manager.clear_session()
            print_success("Logged out")
    
    def cmd_auth_whoami(self, args):
        """Show current user information"""
        self.require_auth()
        
        try:
            user = self.client.get_current_user()
            
            print_title("Current User Information")
            print(f"  ID:         {user['id']}")
            print(f"  Username:   {Colors.GREEN}{user['username']}{Colors.NC}")
            print(f"  Email:      {user['email']}")
            print(f"  Full Name:  {user.get('full_name', 'N/A')}")
            print(f"  Role:       {Colors.CYAN}{user['role']}{Colors.NC}")
            print(f"  Status:     {Colors.GREEN}{user['status']}{Colors.NC}")
            print(f"  Company:    {user.get('company', 'N/A')}")
            print(f"  Created:    {user['created_at']}")
            if user.get('last_login'):
                print(f"  Last Login: {user['last_login']}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    # ========================================================================
    # Log Commands
    # ========================================================================
    
    def cmd_logs_list(self, args):
        """List logs"""
        self.require_auth()
        
        try:
            limit = int(args[0]) if len(args) > 0 else 20
            logs = self.client.get_my_logs(limit=limit)
            
            print_title(f"Recent Logs (Last {len(logs)})")
            
            if not logs:
                print_warning("No logs found")
                return
            
            headers = ["ID", "Level", "Message", "Time"]
            rows = []
            for log in logs:
                message = log['message'][:50] + "..." if len(log['message']) > 50 else log['message']
                created = datetime.fromisoformat(log['created_at'].replace('Z', '+00:00'))
                rows.append([
                    log['id'],
                    log['level'].upper(),
                    message,
                    created.strftime("%Y-%m-%d %H:%M")
                ])
            
            print_table(headers, rows)
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_logs_stats(self, args):
        """Show log statistics"""
        self.require_auth()
        
        try:
            hours = int(args[0]) if len(args) > 0 else 24
            stats = self.client.get_log_stats(hours=hours)
            
            print_title(f"Log Statistics ({stats['time_period']})")
            print(f"  Total Logs:   {stats['total_logs']}")
            print(f"  Error Rate:   {stats['error_rate']:.2f}%")
            if stats.get('avg_response_time_ms'):
                print(f"  Avg Response: {stats['avg_response_time_ms']:.2f}ms")
            
            print(f"\n{Colors.BOLD}By Level:{Colors.NC}")
            for level, count in stats['by_level'].items():
                print(f"    {level.upper():10} {count:5}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    # ========================================================================
    # Report Commands
    # ========================================================================
    
    def cmd_reports_list(self, args):
        """List reports"""
        self.require_auth()
        
        try:
            limit = int(args[0]) if len(args) > 0 else 20
            reports = self.client.get_reports(limit=limit)
            
            print_title(f"Your Reports (Last {len(reports)})")
            
            if not reports:
                print_warning("No reports found")
                return
            
            headers = ["ID", "Name", "Type", "Status", "Progress", "Created"]
            rows = []
            for report in reports:
                created = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00'))
                rows.append([
                    report['id'],
                    report['name'][:30],
                    report['report_type'],
                    report['status'],
                    f"{report['progress']:.0f}%",
                    created.strftime("%Y-%m-%d %H:%M")
                ])
            
            print_table(headers, rows)
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_reports_create(self, args):
        """Create a new report"""
        self.require_auth()
        
        print_title("Create New Report")
        
        name = input("Report Name: ").strip()
        report_type = input("Report Type (fraud_detection/analytics/risk_analysis): ").strip()
        description = input("Description (optional): ").strip() or None
        
        try:
            report = self.client.create_report(
                name=name,
                report_type=report_type,
                description=description
            )
            print_success(f"Report created with ID: {report['id']}")
            print_info(f"Status: {report['status']}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_reports_view(self, args):
        """View report details"""
        self.require_auth()
        
        if len(args) == 0:
            print_error("Usage: dafu reports view <report_id>")
            return
        
        try:
            report_id = int(args[0])
            report = self.client.get_report(report_id)
            
            print_title(f"Report Details - {report['name']}")
            print(f"  ID:           {report['id']}")
            print(f"  Name:         {report['name']}")
            print(f"  Type:         {report['report_type']}")
            print(f"  Status:       {Colors.CYAN}{report['status']}{Colors.NC}")
            print(f"  Progress:     {report['progress']:.0f}%")
            print(f"  Created:      {report['created_at']}")
            
            if report.get('completed_at'):
                print(f"  Completed:    {report['completed_at']}")
            
            if report.get('processing_time_seconds'):
                print(f"  Processing:   {report['processing_time_seconds']:.2f}s")
            
            if report.get('total_records'):
                print(f"  Records:      {report['total_records']}")
            
            if report.get('results'):
                print(f"\n{Colors.BOLD}Results:{Colors.NC}")
                print(json.dumps(report['results'], indent=2))
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_reports_stats(self, args):
        """Show report statistics"""
        self.require_auth()
        
        try:
            stats = self.client.get_report_stats()
            
            print_title("Report Statistics")
            print(f"  Total Reports:  {stats['total_reports']}")
            print(f"  Success Rate:   {stats['success_rate']:.1f}%")
            
            if stats.get('avg_processing_time_seconds'):
                print(f"  Avg Processing: {stats['avg_processing_time_seconds']:.2f}s")
            
            print(f"\n{Colors.BOLD}By Status:{Colors.NC}")
            for status, count in stats['by_status'].items():
                print(f"    {status:12} {count:5}")
            
            print(f"\n{Colors.BOLD}By Type:{Colors.NC}")
            for rtype, count in stats['by_type'].items():
                print(f"    {rtype:20} {count:5}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    # ========================================================================
    # Product Commands
    # ========================================================================
    
    def cmd_products_list(self, args):
        """List products"""
        self.require_auth()
        
        try:
            limit = int(args[0]) if len(args) > 0 else 20
            products = self.client.get_products(limit=limit)
            
            print_title(f"Products (Last {len(products)})")
            
            if not products:
                print_warning("No products found")
                return
            
            headers = ["ID", "SKU", "Name", "Price", "Stock", "Risk", "Status"]
            rows = []
            for product in products:
                rows.append([
                    product['id'],
                    product['sku'],
                    product['name'][:30],
                    f"${product['price']:.2f}",
                    product['stock_quantity'],
                    f"{product['fraud_risk_score']:.2f}",
                    product['status']
                ])
            
            print_table(headers, rows)
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_products_high_risk(self, args):
        """List high-risk products"""
        self.require_auth()
        
        try:
            limit = int(args[0]) if len(args) > 0 else 20
            products = self.client.get_high_risk_products(limit=limit)
            
            print_title(f"High-Risk Products ({len(products)})")
            
            if not products:
                print_success("No high-risk products found!")
                return
            
            headers = ["ID", "SKU", "Name", "Risk Score", "Incidents"]
            rows = []
            for product in products:
                rows.append([
                    product['id'],
                    product['sku'],
                    product['name'][:30],
                    f"{Colors.RED}{product['fraud_risk_score']:.2f}{Colors.NC}",
                    product['fraud_incidents']
                ])
            
            print_table(headers, rows)
        except Exception as e:
            print_error(f"Error: {e}")
    
    def cmd_products_stats(self, args):
        """Show product statistics"""
        self.require_auth()
        
        try:
            stats = self.client.get_product_stats()
            
            print_title("Product Statistics")
            print(f"  Total Products:   {stats['total_products']}")
            print(f"  High Risk:        {stats['high_risk_count']}")
            print(f"  Low Stock:        {stats['low_stock_count']}")
            print(f"  Total Value:      ${stats['total_value']:,.2f}")
            print(f"  Average Price:    ${stats['avg_price']:.2f}")
            
            print(f"\n{Colors.BOLD}By Status:{Colors.NC}")
            for status, count in stats['by_status'].items():
                print(f"    {status:12} {count:5}")
        except Exception as e:
            print_error(f"Error: {e}")
    
    # ========================================================================
    # Main Command Handler
    # ========================================================================
    
    def run(self, args):
        """Run CLI command"""
        if len(args) == 0:
            self.cmd_help([])
            return
        
        command = args[0].lower()
        sub_args = args[1:]
        
        # Command routing
        commands = {
            'auth': {
                'register': self.cmd_auth_register,
                'login': self.cmd_auth_login,
                'logout': self.cmd_auth_logout,
                'whoami': self.cmd_auth_whoami,
            },
            'logs': {
                'list': self.cmd_logs_list,
                'stats': self.cmd_logs_stats,
            },
            'reports': {
                'list': self.cmd_reports_list,
                'create': self.cmd_reports_create,
                'view': self.cmd_reports_view,
                'stats': self.cmd_reports_stats,
            },
            'products': {
                'list': self.cmd_products_list,
                'high-risk': self.cmd_products_high_risk,
                'stats': self.cmd_products_stats,
            },
        }
        
        if command in commands:
            if len(sub_args) == 0:
                print_error(f"Usage: dafu {command} <subcommand>")
                print_info(f"Available subcommands: {', '.join(commands[command].keys())}")
                return
            
            subcommand = sub_args[0].lower()
            if subcommand in commands[command]:
                commands[command][subcommand](sub_args[1:])
            else:
                print_error(f"Unknown subcommand: {subcommand}")
                print_info(f"Available subcommands: {', '.join(commands[command].keys())}")
        elif command == 'help':
            self.cmd_help(sub_args)
        else:
            print_error(f"Unknown command: {command}")
            self.cmd_help([])
    
    def cmd_help(self, args):
        """Show help"""
        print_title("DAFU CLI - Help")
        
        print(f"{Colors.BOLD}Authentication:{Colors.NC}")
        print("  dafu auth register        - Register a new user")
        print("  dafu auth login           - Login to DAFU")
        print("  dafu auth logout          - Logout from DAFU")
        print("  dafu auth whoami          - Show current user")
        
        print(f"\n{Colors.BOLD}Logs:{Colors.NC}")
        print("  dafu logs list [limit]    - List logs")
        print("  dafu logs stats [hours]   - Show log statistics")
        
        print(f"\n{Colors.BOLD}Reports:{Colors.NC}")
        print("  dafu reports list [limit] - List reports")
        print("  dafu reports create       - Create a new report")
        print("  dafu reports view <id>    - View report details")
        print("  dafu reports stats        - Show report statistics")
        
        print(f"\n{Colors.BOLD}Products:{Colors.NC}")
        print("  dafu products list [limit]    - List products")
        print("  dafu products high-risk [limit] - List high-risk products")
        print("  dafu products stats           - Show product statistics")
        
        print(f"\n{Colors.BOLD}General:{Colors.NC}")
        print("  dafu help                 - Show this help message")
        print()


def main():
    """Main entry point"""
    cli = DAFUCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()

