#!/usr/bin/env python3
"""
CordysCRM REST API Test Script

This script tests all REST API endpoints of CordysCRM to ensure they are accessible and functional.

Usage:
    python test-restapi.py [options]

Options:
    --base-url URL    Base URL of the API (default: http://127.0.0.1:8081)
    --username USER    Username (default: admin)
    --password PASS   Password (default: CordysCRM)
    --org-id ID       Organization ID (default: 100001)
    --verbose         Enable verbose output
    --timeout SEC     Request timeout in seconds (default: 30)
    --output FILE     Save test results to JSON file
"""

import argparse
import json
import sys
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib3

try:
    import requests
except ImportError:
    print("Error: requests module is required. Install with: pip install requests")
    sys.exit(1)

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@dataclass
class TestResult:
    """Represents the result of a single API test."""
    module: str
    endpoint: str
    method: str
    success: bool
    status_code: int
    response_time_ms: float
    error_message: str = ""
    response_body: Any = None

    def to_dict(self) -> Dict:
        return asdict(self)


class CordysCRMTester:
    """CordysCRM API Tester"""

    def __init__(self, base_url: str, username: str, password: str, org_id: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.org_id = org_id
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = False
        self.session.headers.update({
            'Organization-Id': org_id,
            'Content-Type': 'application/json'
        })
        self.results: List[TestResult] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    def test_get(self, path: str, module: str, description: str = "") -> TestResult:
        """Test a GET endpoint."""
        url = f"{self.base_url}{path}"
        desc = description or path
        self.log(f"Testing GET {path} ({desc})")

        try:
            import time
            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout)
            elapsed_time = (time.time() - start_time) * 1000

            result = TestResult(
                module=module,
                endpoint=path,
                method="GET",
                success=response.status_code == 200,
                status_code=response.status_code,
                response_time_ms=elapsed_time,
                response_body=self._safe_parse_json(response.text) if response.text else None
            )

            if response.status_code == 200:
                self.log(f"  ✓ OK ({response.status_code}) - {elapsed_time:.0f}ms", "SUCCESS")
            else:
                result.error_message = f"Expected 200, got {response.status_code}"
                self.log(f"  ✗ FAILED ({response.status_code}) - {result.error_message}", "ERROR")

            self.results.append(result)
            return result

        except requests.exceptions.Timeout:
            result = TestResult(
                module=module,
                endpoint=path,
                method="GET",
                success=False,
                status_code=0,
                response_time_ms=self.timeout * 1000,
                error_message="Request timeout"
            )
            self.log(f"  ✗ TIMEOUT after {self.timeout}s", "ERROR")
            self.results.append(result)
            return result

        except Exception as e:
            result = TestResult(
                module=module,
                endpoint=path,
                method="GET",
                success=False,
                status_code=0,
                response_time_ms=0,
                error_message=str(e)
            )
            self.log(f"  ✗ ERROR: {e}", "ERROR")
            self.results.append(result)
            return result

    def test_post(self, path: str, data: Dict, module: str, description: str = "") -> TestResult:
        """Test a POST endpoint."""
        url = f"{self.base_url}{path}"
        desc = description or path
        self.log(f"Testing POST {path} ({desc})")

        try:
            import time
            start_time = time.time()
            response = self.session.post(url, json=data, timeout=self.timeout)
            elapsed_time = (time.time() - start_time) * 1000

            result = TestResult(
                module=module,
                endpoint=path,
                method="POST",
                success=response.status_code == 200,
                status_code=response.status_code,
                response_time_ms=elapsed_time,
                response_body=self._safe_parse_json(response.text) if response.text else None
            )

            if response.status_code == 200:
                self.log(f"  ✓ OK ({response.status_code}) - {elapsed_time:.0f}ms", "SUCCESS")
            else:
                result.error_message = f"Expected 200, got {response.status_code}"
                self.log(f"  ✗ FAILED ({response.status_code}) - {result.error_message}", "ERROR")

            self.results.append(result)
            return result

        except requests.exceptions.Timeout:
            result = TestResult(
                module=module,
                endpoint=path,
                method="POST",
                success=False,
                status_code=0,
                response_time_ms=self.timeout * 1000,
                error_message="Request timeout"
            )
            self.log(f"  ✗ TIMEOUT after {self.timeout}s", "ERROR")
            self.results.append(result)
            return result

        except Exception as e:
            result = TestResult(
                module=module,
                endpoint=path,
                method="POST",
                success=False,
                status_code=0,
                response_time_ms=0,
                error_message=str(e)
            )
            self.log(f"  ✗ ERROR: {e}", "ERROR")
            self.results.append(result)
            return result

    def _safe_parse_json(self, text: str) -> Any:
        """Safely parse JSON response."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    def run_all_tests(self):
        """Run all API tests."""
        self.log("=" * 60)
        self.log("CordysCRM REST API Test Suite")
        self.log("=" * 60)
        self.log(f"Base URL: {self.base_url}")
        self.log(f"Username: {self.username}")
        self.log(f"Organization ID: {self.org_id}")
        self.log("=" * 60)
        print()

        # 1. Basic Health Check
        self._test_basic_health()

        # 2. Home Statistics
        self._test_home_statistics()

        # 3. Dashboard Module
        self._test_dashboard_module()

        # 4. Customer Module
        self._test_customer_module()

        # 5. Customer Pool Module
        self._test_customer_pool_module()

        # 6. Clue Module
        self._test_clue_module()

        # 7. Opportunity Module
        self._test_opportunity_module()

        # 8. Product Module
        self._test_product_module()

        # 9. Contract Module
        self._test_contract_module()

        # 10. Invoice Module
        self._test_invoice_module()

        # 11. View Management
        self._test_view_management()

        # 12. Search Module
        self._test_search_module()

        # 13. Follow Up Module
        self._test_follow_up_module()

        # 14. System Module
        self._test_system_module()

        # 15. Organization Module
        self._test_organization_module()

        # 16. Role & Permission Module
        self._test_role_permission_module()

        # 17. Message & Notification Module
        self._test_message_notification_module()

        # 18. Personal Center Module
        self._test_personal_center_module()

        # 19. File Management Module
        self._test_file_management_module()

        # 20. Agent Module
        self._test_agent_module()

        self._print_summary()

    def _test_basic_health(self):
        """Test basic health endpoints."""
        self.log("\n[1/20] Basic Health Check")
        self.log("-" * 60)

        self.test_get("/v3/api-docs", "Health", "OpenAPI docs")

        # Swagger UI
        try:
            response = self.session.get(f"{self.base_url}/swagger-ui/index.html", timeout=self.timeout)
            if response.status_code in [200, 302]:
                self.log(f"  ✓ Swagger UI OK ({response.status_code})", "SUCCESS")
            else:
                self.log(f"  ✗ Swagger UI FAILED ({response.status_code})", "ERROR")
        except Exception as e:
            self.log(f"  ✗ Swagger UI ERROR: {e}", "ERROR")

        self.test_get("/system/version", "Health", "System version")
        self.test_post("/locale-language/change", {"language": "zh_CN"}, "Health", "Locale language change")

    def _test_home_statistics(self):
        """Test home statistics endpoints."""
        self.log("\n[2/20] Home Statistics")
        self.log("-" * 60)

        self.test_post("/home/statistic/lead", {}, "Home", "Lead statistics")
        self.test_post("/home/statistic/opportunity", {}, "Home", "Opportunity statistics")
        self.test_post("/home/statistic/opportunity/underway", {}, "Home", "Underway opportunity statistics")
        self.test_post("/home/statistic/opportunity/success", {}, "Home", "Success opportunity statistics")
        self.test_get("/home/statistic/department/tree", "Home", "Department tree")

    def _test_dashboard_module(self):
        """Test dashboard module endpoints."""
        self.log("\n[3/20] Dashboard Module")
        self.log("-" * 60)

        self.test_get("/dashboard/module/tree", "Dashboard", "Module tree")
        self.test_get("/dashboard/module/count", "Dashboard", "Module count")

    def _test_customer_module(self):
        """Test customer module endpoints."""
        self.log("\n[4/20] Customer Module")
        self.log("-" * 60)

        self.test_get("/account/module/form", "Customer", "Form config")
        self.test_post("/account/page", {"current": 1, "pageSize": 1}, "Customer", "Page")
        self.test_post("/account/option", {"current": 1, "pageSize": 10, "keyword": ""}, "Customer", "Options")
        self.test_get("/account/tab", "Customer", "Tab config")

        self.test_post("/account/contact/page", {"current": 1, "pageSize": 1}, "Customer", "Contact page")
        self.test_get("/account/contact/module/form", "Customer", "Contact form config")
        self.test_get("/account/contact/tab", "Customer", "Contact tab")

        self.test_post("/account/follow/record/page", {"current": 1, "pageSize": 1}, "Customer", "Follow record page")
        self.test_post("/account/follow/plan/page", {"current": 1, "pageSize": 1}, "Customer", "Follow plan page")

        self.test_post("/account/contract/page", {"current": 1, "pageSize": 1}, "Customer", "Contract page")
        self.test_post("/account/contract/payment-plan/page", {"current": 1, "pageSize": 1}, "Customer", "Payment plan page")
        self.test_post("/account/contract/payment-record/page", {"current": 1, "pageSize": 1}, "Customer", "Payment record page")
        self.test_post("/account/invoice/page", {"current": 1, "pageSize": 1}, "Customer", "Invoice page")

    def _test_customer_pool_module(self):
        """Test customer pool module endpoints."""
        self.log("\n[5/20] Customer Pool Module")
        self.log("-" * 60)

        self.test_post("/account-pool/page", {"current": 1, "pageSize": 1}, "CustomerPool", "Page")
        self.test_post("/pool/account/page", {"current": 1, "pageSize": 1}, "CustomerPool", "Customer page")
        self.test_get("/pool/account/options", "CustomerPool", "Options")

    def _test_clue_module(self):
        """Test clue module endpoints."""
        self.log("\n[6/20] Clue (Lead) Module")
        self.log("-" * 60)

        self.test_get("/lead/module/form", "Clue", "Form config")
        self.test_post("/lead/page", {"current": 1, "pageSize": 1}, "Clue", "Page")
        self.test_get("/lead/tab", "Clue", "Tab config")

        self.test_post("/lead/follow/record/page", {"current": 1, "pageSize": 1}, "Clue", "Follow record page")
        self.test_post("/lead/follow/plan/page", {"current": 1, "pageSize": 1}, "Clue", "Follow plan page")

        self.test_post("/lead-pool/page", {"current": 1, "pageSize": 1}, "Clue", "Pool page")
        self.test_post("/pool/lead/page", {"current": 1, "pageSize": 1}, "Clue", "Pool lead page")
        self.test_get("/pool/lead/options", "Clue", "Pool options")

    def _test_opportunity_module(self):
        """Test opportunity module endpoints."""
        self.log("\n[7/20] Opportunity Module")
        self.log("-" * 60)

        self.test_get("/opportunity/module/form", "Opportunity", "Form config")
        self.test_post("/opportunity/page", {"current": 1, "pageSize": 1}, "Opportunity", "Page")
        self.test_post("/opportunity/statistic", {"viewId": "ALL"}, "Opportunity", "Statistic")
        self.test_get("/opportunity/tab", "Opportunity", "Tab config")

        self.test_post("/opportunity/follow/record/page", {"current": 1, "pageSize": 1}, "Opportunity", "Follow record page")
        self.test_post("/opportunity/follow/plan/page", {"current": 1, "pageSize": 1}, "Opportunity", "Follow plan page")

        self.test_get("/opportunity/stage/get", "Opportunity", "Stage config")

    def _test_product_module(self):
        """Test product module endpoints."""
        self.log("\n[8/20] Product Module")
        self.log("-" * 60)

        self.test_get("/product/module/form", "Product", "Form config")
        self.test_post("/product/page", {"current": 1, "pageSize": 1}, "Product", "Page")
        self.test_get("/product/list/option", "Product", "Options")

        self.test_post("/price/page", {"current": 1, "pageSize": 1}, "Product", "Price page")
        self.test_get("/price/module/form", "Product", "Price form config")

    def _test_contract_module(self):
        """Test contract module endpoints."""
        self.log("\n[9/20] Contract Module")
        self.log("-" * 60)

        self.test_get("/contract/module/form", "Contract", "Form config")
        self.test_post("/contract/page", {"current": 1, "pageSize": 1}, "Contract", "Page")
        self.test_get("/contract/tab", "Contract", "Tab config")

        self.test_post("/contract/payment-plan/page", {"current": 1, "pageSize": 1}, "Contract", "Payment plan page")
        self.test_get("/contract/payment-plan/module/form", "Contract", "Payment plan form config")
        self.test_get("/contract/payment-plan/tab", "Contract", "Payment plan tab")

        self.test_post("/contract/payment-record/page", {"current": 1, "pageSize": 1}, "Contract", "Payment record page")
        self.test_get("/contract/payment-record/module/form", "Contract", "Payment record form config")
        self.test_get("/contract/payment-record/tab", "Contract", "Payment record tab")

        self.test_post("/contract/business-title/page", {"current": 1, "pageSize": 1}, "Contract", "Business title page")

    def _test_invoice_module(self):
        """Test invoice module endpoints."""
        self.log("\n[10/20] Invoice Module")
        self.log("-" * 60)

        self.test_post("/invoice/page", {"current": 1, "pageSize": 1}, "Invoice", "Page")
        self.test_get("/invoice/module/form", "Invoice", "Form config")
        self.test_get("/invoice/tab", "Invoice", "Tab")

    def _test_view_management(self):
        """Test view management endpoints."""
        self.log("\n[11/20] View Management")
        self.log("-" * 60)

        self.test_get("/account/view/list", "View", "Customer view list")
        self.test_get("/account/contact/view/list", "View", "Customer contact view list")
        self.test_get("/pool/account/view/list", "View", "Pool customer view list")

        self.test_get("/lead/view/list", "View", "Clue view list")
        self.test_get("/pool/lead/view/list", "View", "Pool lead view list")

        self.test_get("/opportunity/view/list", "View", "Opportunity view list")

        self.test_get("/contract/view/list", "View", "Contract view list")
        self.test_get("/contract/payment-plan/view/list", "View", "Payment plan view list")
        self.test_get("/contract/payment-record/view/list", "View", "Payment record view list")
        self.test_get("/invoice/view/list", "View", "Invoice view list")

    def _test_search_module(self):
        """Test search module endpoints."""
        self.log("\n[12/20] Search Module")
        self.log("-" * 60)

        self.test_post("/global/search/account", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search customer")
        self.test_post("/global/search/customer_pool", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search customer pool")
        self.test_post("/global/search/contact", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search contact")
        self.test_post("/global/search/lead", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search lead")
        self.test_post("/global/search/clue_pool", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search clue pool")
        self.test_post("/global/search/opportunity", {"current": 1, "pageSize": 1, "keyword": ""}, "Search", "Global search opportunity")

        self.test_post("/advanced/search/account", {"current": 1, "pageSize": 1}, "Search", "Advanced search customer")
        self.test_post("/advanced/search/account-pool", {"current": 1, "pageSize": 1}, "Search", "Advanced search customer pool")
        self.test_post("/advanced/search/contact", {"current": 1, "pageSize": 1}, "Search", "Advanced search contact")
        self.test_post("/advanced/search/lead", {"current": 1, "pageSize": 1}, "Search", "Advanced search lead")
        self.test_post("/advanced/search/lead-pool", {"current": 1, "pageSize": 1}, "Search", "Advanced search lead pool")
        self.test_post("/advanced/search/opportunity", {"current": 1, "pageSize": 1}, "Search", "Advanced search opportunity")

        self.test_get("/global/search/module/count", "Search", "Module count")

    def _test_follow_up_module(self):
        """Test follow up module endpoints."""
        self.log("\n[13/20] Follow Up Module")
        self.log("-" * 60)

        self.test_post("/follow/record/page", {"current": 1, "pageSize": 1}, "Follow", "Record page")
        self.test_get("/follow/record/tab", "Follow", "Record tab")

        self.test_post("/follow/plan/page", {"current": 1, "pageSize": 1}, "Follow", "Plan page")
        self.test_get("/follow/plan/tab", "Follow", "Plan tab")

        self.test_get("/follow/record/view/list", "Follow", "Record view list")
        self.test_get("/follow/plan/view/list", "Follow", "Plan view list")

    def _test_system_module(self):
        """Test system module endpoints."""
        self.log("\n[14/20] System Module")
        self.log("-" * 60)

        self.test_get("/module/list", "System", "Module list")
        self.test_get("/module/user/dept/tree", "System", "User dept tree")
        self.test_get("/module/role/tree", "System", "Role tree")
        self.test_get("/module/advanced-search/settings", "System", "Advanced search settings")

        self.test_get("/dict/get/ACCOUNT", "System", "Dict get (account)")
        self.test_get("/dict/config", "System", "Dict config")

        self.test_get("/search/config/get", "System", "Search config")
        self.test_get("/mask/config/get", "System", "Mask config")

        self.test_get("/navigation/list", "System", "Navigation list")

    def _test_organization_module(self):
        """Test organization module endpoints."""
        self.log("\n[15/20] Organization Module")
        self.log("-" * 60)

        self.test_get("/department/tree", "Organization", "Department tree")

    def _test_role_permission_module(self):
        """Test role and permission module endpoints."""
        self.log("\n[16/20] Role & Permission Module")
        self.log("-" * 60)

        self.test_get("/role/list", "Role", "List")
        self.test_get("/role/user/dept/tree", "Role", "User dept tree")
        self.test_get("/role/dept/tree", "Role", "Dept tree")

    def _test_message_notification_module(self):
        """Test message and notification module endpoints."""
        self.log("\n[17/20] Message & Notification Module")
        self.log("-" * 60)

        self.test_post("/notification/list/all/page", {"current": 1, "pageSize": 10}, "Message", "Notification list")
        self.test_get("/notification/count", "Message", "Notification count")

    def _test_personal_center_module(self):
        """Test personal center module endpoints."""
        self.log("\n[18/20] Personal Center Module")
        self.log("-" * 60)

        self.test_get("/personal/center/info", "Personal", "Center info")
        self.test_post("/personal/center/follow/plan/list", {"current": 1, "pageSize": 10}, "Personal", "Follow plan list")

        self.test_post("/export/center/list", {"current": 1, "pageSize": 10}, "Personal", "Export center list")

        self.test_get("/user/api/key/list", "Personal", "API key list")

    def _test_file_management_module(self):
        """Test file management module endpoints."""
        self.log("\n[19/20] File Management Module")
        self.log("-" * 60)

        # Note: These will fail without actual files, but we test the endpoint existence
        self.test_post("/pic/upload/temp", {}, "File", "Upload temp pic (empty test)")
        self.test_post("/attachment/upload/temp", {}, "File", "Upload temp attachment (empty test)")

    def _test_agent_module(self):
        """Test agent module endpoints."""
        self.log("\n[20/20] Agent Module")
        self.log("-" * 60)

        self.test_post("/agent/page", {"current": 1, "pageSize": 10}, "Agent", "Page")
        self.test_get("/agent/option", "Agent", "Options")
        self.test_get("/agent/module/tree", "Agent", "Module tree")
        self.test_get("/agent/module/count", "Agent", "Module count")

    def _print_summary(self):
        """Print test summary."""
        print()
        self.log("=" * 60)
        self.log("Test Summary")
        self.log("=" * 60)

        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print()
            self.log("Failed Tests:", "ERROR")
            self.log("-" * 60)
            for result in self.results:
                if not result.success:
                    self.log(f"  [{result.module}] {result.method} {result.endpoint}")
                    self.log(f"    Status: {result.status_code}")
                    self.log(f"    Error: {result.error_message}")

        print()
        self.log("=" * 60)
        if failed == 0:
            self.log("✓ All tests passed!", "SUCCESS")
        else:
            self.log("✗ Some tests failed", "ERROR")
        self.log("=" * 60)

    def save_results(self, filename: str):
        """Save test results to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2, ensure_ascii=False)
        self.log(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='CordysCRM REST API Test Script')
    parser.add_argument('--base-url', default='http://127.0.0.1:8081',
                        help='Base URL of the API (default: http://127.0.0.1:8081)')
    parser.add_argument('--username', default='admin',
                        help='Username (default: admin)')
    parser.add_argument('--password', default='CordysCRM',
                        help='Password (default: CordysCRM)')
    parser.add_argument('--org-id', default='100001',
                        help='Organization ID (default: 100001)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--timeout', type=int, default=30,
                        help='Request timeout in seconds (default: 30)')
    parser.add_argument('--output', type=str,
                        help='Save test results to JSON file')

    args = parser.parse_args()

    tester = CordysCRMTester(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        org_id=args.org_id,
        timeout=args.timeout
    )

    tester.run_all_tests()

    if args.output:
        tester.save_results(args.output)

    # Exit with error code if any tests failed
    failed = sum(1 for r in tester.results if not r.success)
    sys.exit(1 if failed > 0 else 0)


if __name__ == '__main__':
    main()
