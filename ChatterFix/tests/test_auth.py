"""
Unit Tests for Authentication and Role-Based Access Control (RBAC).

This test suite verifies the core security logic in `frontend.auth_utils`.
It uses mocking to simulate Streamlit's session state, allowing for
isolated testing of the authorization logic.
"""
import unittest
from unittest.mock import MagicMock

import streamlit as st
from frontend import auth_utils


class TestAuthUtils(unittest.TestCase):
    """Test suite for auth_utils.py"""

    def setUp(self):
        """Reset mocks before each test."""
        st.session_state = {}

    # --- Tests for is_logged_in() ---

    def test_is_logged_in_true(self):
        """Verify is_logged_in returns True when user is in session."""
        st.session_state['user'] = MagicMock()
        self.assertTrue(auth_utils.is_logged_in())

    def test_is_logged_in_false_no_user(self):
        """Verify is_logged_in returns False when user is not in session."""
        self.assertFalse(auth_utils.is_logged_in())

    def test_is_logged_in_false_user_is_none(self):
        """Verify is_logged_in returns False when user is None."""
        st.session_state['user'] = None
        self.assertFalse(auth_utils.is_logged_in())

    # --- Tests for has_permission() ---

    def test_has_permission_not_logged_in(self):
        """Verify has_permission returns False if user is not logged in."""
        self.assertFalse(auth_utils.has_permission('admin'))

    def test_has_permission_admin_success(self):
        """Verify admin has permission for admin role."""
        st.session_state['user'] = MagicMock(role='admin')
        self.assertTrue(auth_utils.has_permission('admin'))

    def test_has_permission_manager_for_manager_success(self):
        """Verify manager has permission for manager role."""
        st.session_state['user'] = MagicMock(role='manager')
        self.assertTrue(auth_utils.has_permission('manager'))

    def test_has_permission_admin_for_manager_success(self):
        """Verify admin has permission for manager role."""
        st.session_state['user'] = MagicMock(role='admin')
        self.assertTrue(auth_utils.has_permission('manager'))

    def test_has_permission_technician_for_technician_success(self):
        """Verify technician has permission for technician role."""
        st.session_state['user'] = MagicMock(role='technician')
        self.assertTrue(auth_utils.has_permission('technician'))

    def test_has_permission_manager_for_technician_success(self):
        """Verify manager has permission for technician role."""
        st.session_state['user'] = MagicMock(role='manager')
        self.assertTrue(auth_utils.has_permission('technician'))

    def test_has_permission_admin_for_technician_success(self):
        """Verify admin has permission for technician role."""
        st.session_state['user'] = MagicMock(role='admin')
        self.assertTrue(auth_utils.has_permission('technician'))

    def test_has_permission_technician_for_manager_failure(self):
        """Verify technician does not have permission for manager role."""
        st.session_state['user'] = MagicMock(role='technician')
        self.assertFalse(auth_utils.has_permission('manager'))

    def test_has_permission_technician_for_admin_failure(self):
        """Verify technician does not have permission for admin role."""
        st.session_state['user'] = MagicMock(role='technician')
        self.assertFalse(auth_utils.has_permission('admin'))

    def test_has_permission_manager_for_admin_failure(self):
        """Verify manager does not have permission for admin role."""
        st.session_state['user'] = MagicMock(role='manager')
        self.assertFalse(auth_utils.has_permission('admin'))


if __name__ == '__main__':
    unittest.main()
