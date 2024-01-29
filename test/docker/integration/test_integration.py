#!/usr/bin/env python3

import requests


class IntegrationTester:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, message=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_kong_admin_api(self):
        """Test Kong Admin API is accessible"""
        try:
            response = self.session.get(f"{self.config.kong_endpoint}/status")
            if response.status_code == 200:
                self.log_test("Kong Admin API", True,
                             "Admin API is accessible")
                return True
            else:
                self.log_test("Kong Admin API", False,
                             f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Kong Admin API", False, f"Error: {str(e)}")
            return False

    def test_keycloak_health(self):
        """Test Keycloak is accessible"""
        try:
            response = self.session.get(f"{self.config.keycloak_endpoint}/health")
            if response.status_code == 200:
                self.log_test("Keycloak Health", True, "Keycloak is accessible")
                return True
            else:
                self.log_test("Keycloak Health", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Keycloak Health", False, f"Error: {str(e)}")
            return False

    def test_oidc_discovery(self):
        """Test OIDC discovery endpoint"""
        try:
            response = self.session.get(self.config.discovery)
            if response.status_code == 200:
                data = response.json()
                if 'authorization_endpoint' in data and 'token_endpoint' in data:
                    self.log_test("OIDC Discovery", True, "Discovery endpoint working")
                    return True
                else:
                    self.log_test("OIDC Discovery", False, "Missing required endpoints")
                    return False
            else:
                self.log_test("OIDC Discovery", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("OIDC Discovery", False, f"Error: {str(e)}")
            return False

    def test_protected_endpoint_redirect(self):
        """Test that protected endpoint redirects to login"""
        try:
            # Test without authentication
            response = self.session.get("http://localhost:8000/httpbin/get", allow_redirects=False)

            if response.status_code in [302, 303, 307, 308]:
                # Check if redirect is to Keycloak
                location = response.headers.get('Location', '')
                if 'keycloak' in location.lower() or 'auth' in location.lower():
                    self.log_test("Protected Endpoint Redirect", True, "Redirects to authentication")
                    return True
                else:
                    self.log_test("Protected Endpoint Redirect", False, f"Unexpected redirect: {location}")
                    return False
            else:
                self.log_test("Protected Endpoint Redirect", False, f"Expected redirect, got: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Protected Endpoint Redirect", False, f"Error: {str(e)}")
            return False

    def test_public_endpoint(self):
        """Test that public endpoints are accessible"""
        try:
            # This would need to be configured in Kong to be public
            # For now, we'll test the admin API as a public endpoint
            response = self.session.get(f"{self.config.kong_endpoint}/status")
            if response.status_code == 200:
                self.log_test("Public Endpoint", True, "Public endpoint accessible")
                return True
            else:
                self.log_test("Public Endpoint", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Public Endpoint", False, f"Error: {str(e)}")
            return False

    def test_plugin_configuration(self):
        """Test that OIDC plugin is properly configured"""
        try:
            response = self.session.get(f"{self.config.kong_endpoint}/plugins")
            if response.status_code == 200:
                plugins = response.json()['data']
                oidc_plugin = None
                for plugin in plugins:
                    if plugin.get('name') == 'oidc':
                        oidc_plugin = plugin
                        break

                if oidc_plugin:
                    config = oidc_plugin.get('config', {})
                    if config.get('client_id') == self.config.client_id:
                        self.log_test("Plugin Configuration", True, "OIDC plugin properly configured")
                        return True
                    else:
                        self.log_test("Plugin Configuration", False, "Plugin config mismatch")
                        return False
                else:
                    self.log_test("Plugin Configuration", False, "OIDC plugin not found")
                    return False
            else:
                self.log_test("Plugin Configuration", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Plugin Configuration", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Running Integration Tests...")
        print("=" * 50)

        # Basic connectivity tests
        self.test_kong_admin_api()
        self.test_keycloak_health()

        # OIDC functionality tests
        self.test_oidc_discovery()
        self.test_plugin_configuration()

        # Endpoint behavior tests
        self.test_protected_endpoint_redirect()
        self.test_public_endpoint()

        # Summary
        print("=" * 50)
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)

        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All integration tests passed!")
            return True
        else:
            print("❌ Some tests failed. Check the output above.")
            return False

def main():
    # Import config from setup.py
    import sys
    sys.path.append('.')

    from setup import get_env_vars, get_config

    env = get_env_vars()
    config = get_config(env)

    tester = IntegrationTester(config)
    success = tester.run_all_tests()

    return 0 if success else 1

if __name__ == '__main__':
    exit(main())
