# -*- coding: utf-8 -*-
from selenium_tests.UserDriverTest import UserDriverTest
from selenium.webdriver.common.by import By


class TestContainerInteraction(UserDriverTest):
    def test_start_stop_container(self):
        with self.logged_in():
            self.wait_until_application_list_loaded()

            self.select_application()
            self.start_selected_application()
            self.wait_until_selected_application_running()

            self.open_application_settings()
            self.stop_selected_application()
            self.wait_until_selected_application_stopped()

    def test_focus(self):
        with self.running_container():
            iframe = self.wait_until_element_visible(By.TAG_NAME, "iframe")
            self.assertEqual(iframe, self.driver.switch_to.active_element)

            self.type_text_in_element_located(By.ID, "search-input", "")

            self.assertNotEqual(iframe, self.driver.switch_to.active_element)

            self.select_application()

            self.assertEqual(iframe, self.driver.switch_to.active_element)
