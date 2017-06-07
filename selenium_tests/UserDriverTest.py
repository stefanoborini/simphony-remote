# -*- coding: utf-8 -*-
import contextlib
from selenium_tests.RemoteAppDriverTest import RemoteAppDriverTest
from selenium.webdriver.common.by import By


class UserDriverTest(RemoteAppDriverTest):
    def select_application(self, index=0):
        self.click_element_located(By.ID, "application-entry-{}".format(index))

    def open_application_settings(self):
        self.click_element_located(By.ID, "application-settings")

    def stop_selected_application(self):
        self.click_element_located(By.ID, "stop-button")

    def start_selected_application(self):
        self.click_element_located(By.ID, "start-button")

    def wait_until_selected_application_running(self):
        self.wait_until_element_present(By.ID, "application")

    def wait_until_selected_application_stopped(self):
        self.wait_until_text_inside(By.ID, "start-button", "Start")

    def wait_until_application_list_loaded(self):
        self.wait_until_element_invisible(By.ID, "loading-spinner")

    @contextlib.contextmanager
    def logged_in(self, username="test"):
        self.login(username)
        try:
            yield
        finally:
            self.logout()

    @contextlib.contextmanager
    def running_container(self, index=0):
        with self.logged_in():
            self.wait_until_application_list_loaded()

            self.select_application(index)
            self.start_selected_application()

            try:
                yield
            finally:
                self.select_application(index)
                self.wait_until_selected_application_running()
                self.open_application_settings()
                self.stop_selected_application()
                self.wait_until_selected_application_stopped()
