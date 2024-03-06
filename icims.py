import time

from decouple import config
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from cookie_manager import CookieManager
from scaper import Scraper


class ICIMSAutomation(Scraper):

    def __init__(self, email, password, cookies_path):
        super().__init__()
        self.email = email
        self.password = password
        self.cookie_manager = CookieManager(self.driver, cookies_path)

    def login(self):
        self.logger("class ICIMSAutomation:login", "Logging in to ICIMS")

        try:
            self.driver.get(self.BASE_URL)
            self.wait_for_clickable(
                By.XPATH, "//a[contains(@class, 'icims-15l4veq')]"
            ).click()
            self.wait_for_element(By.NAME, "username").send_keys(self.email)
            self.driver.find_element(By.CLASS_NAME, "_button-login-id").click()
            self.wait_for_element(By.ID, "identifierId").send_keys(self.email)
            self.wait_for_clickable(By.ID, "identifierNext").click()
            self.wait_for_element(By.NAME, "password").send_keys(self.password)
            self.wait_for_clickable(By.ID, "passwordNext").click()
            print("Logged in successfully")
            self.logger("class ICIMSAutomation:login", "Logged in successfully")

        except Exception as e:
            print(f"Exception during login: {str(e)}")
            self.logger("class ICIMSAutomation:login", f"Error: {e}")

    def get_created_job_id(self):
        id_element = self.wait_for_element(By.CSS_SELECTOR, "small.profile-card-id")
        id_number = id_element.text.split()[1]
        return id_number

    def post_job_external(self):
        self.logger(
            "class ICIMSAutomation:post_job_external", "Posting job to external sites"
        )

        try:
            self.wait_for_clickable(By.ID, "RQ_BROADCAST").click()
            self.switch_to_frame("display_frame_left")
            self.wait_for_clickable(By.ID, "RQ_POSTING_TO_ALL_CAREER_SITES").click()
            autocomplete_input = self.wait_for_clickable(By.ID, "posting-autocomplete")
            autocomplete_input.click()
            autocomplete_input.send_keys("External")
            self.wait_for_clickable(
                By.XPATH, "//li[contains(text(), 'External')]"
            ).click()
            autocomplete_input.send_keys(Keys.ENTER)
            self.wait_for_clickable(By.ID, "post-button").click()
            self.logger(
                "class ICIMSAutomation:post_job_external",
                "Job posted to external sites",
            )

        except Exception as e:
            print(f"Exception during posting to external sites: {str(e)}")
            self.logger("class ICIMSAutomation:post_job_external", f"Error: {e}")

    def create_new_job(self, job_template_id):
        self.logger("class ICIMSAutomation:create_new_job", "Creating new job")

        try:
            self.wait_for_clickable(By.ID, "navdropdown_0_-1_0").click()
            self.wait_for_clickable(By.ID, "navdropdown_1_0_1").click()
            self.switch_to_frame("main_body")
            custom_dropdown = self.wait_for_element(
                By.XPATH, "//a[@id='JobProfileFields.JobTemplate_icimsDropdown']"
            )
            self.driver.execute_script("arguments[0].click();", custom_dropdown)
            custom_dropdown.click()
            search_input = self.wait_for_element(
                By.XPATH, "//input[@class='dropdown-search']"
            )
            search_input.send_keys(job_template_id)
            time.sleep(2)
            self.wait_for_clickable(
                By.ID, f"result-selectable_JobProfileFields.JobTemplate_1"
            ).click()
            self.wait_for_clickable(By.ID, "nextButton").click()
            self.wait_for_clickable(By.ID, "finishButton").click()
            created_job_id = self.get_created_job_id()
            print(f"Created job ID: {created_job_id}")
            self.post_job_external()
            self.logger("class ICIMSAutomation:create_new_job", "Job created")

        except Exception as e:
            print(f"Exception during job creation: {str(e)}")
            self.logger("class ICIMSAutomation:create_new_job", f"Error: {e}")

    def remove_old_postings(self, search_templates, job_template_id):
        """Removes old job postings by unposting and moving them to a 'Closed(No fill)' folder."""

        def navigate_to_search_page():
            """Navigates to the search page."""
            self.driver.get("https://jerseystem.icims.com/platform")
            self.wait_for_clickable(By.ID, "navdropdown_0_-1_1").click()
            self.wait_for_clickable(By.ID, "navdropdown_1_1_2").click()

        def select_and_search_template(template_id):
            """Selects a search template and initiates the search."""
            self.switch_to_frame("main_body")
            custom_dropdown = self.wait_for_element(
                By.XPATH, "//a[@id='savedsearchpicker_icimsDropdown']"
            )
            self.driver.execute_script("arguments[0].click();", custom_dropdown)
            custom_dropdown.click()

            search_input = self.wait_for_element(
                By.XPATH, "//input[@class='dropdown-search']"
            )
            search_input.clear()
            search_input.send_keys(template_id)
            time.sleep(2)
            self.wait_for_clickable(
                By.ID, "result-selectable_savedsearchpicker_0"
            ).click()
            time.sleep(2)

            job_template_input = self.wait_for_element(
                By.XPATH, "//input[@placeholder='— Blank —']"
            )
            job_template_input.clear()
            job_template_input.send_keys(job_template_id)
            self.wait_for_clickable(By.ID, "searchSubmitButton").click()
            time.sleep(1)

            # Select all after ensuring the search results have loaded
            self.wait_for_clickable(
                By.XPATH,
                "//button[@class='btn btn-default dropdown-toggle' and @data-toggle='dropdown']",
            ).click()
            self.wait_for_clickable(
                By.XPATH,
                "//a[@class='dropdown-item viewAction' and @title='Select All']",
            ).click()

        def unpost_jobs():
            """Unposts the selected jobs."""
            self.wait_for_clickable(By.ID, "actionPost_anchor").click()
            self.switch_to_new_window()
            try:
                self.wait_for_clickable(By.ID, "UnpostAll3").click()
            except WebDriverException:
                # Fallback selector
                self.wait_for_clickable(By.ID, "3").click()
            self.wait_for_clickable(
                By.XPATH, "//button[.//span[text()='Save']]"
            ).click()
            self.switch_back_to_main_window()

        def move_jobs_to_closed_no_fill():
            """Moves jobs to the 'Closed(No fill)' folder."""
            self.wait_for_clickable(By.ID, "actionBulkEditFields_anchor").click()
            self.switch_to_new_window()
            self.wait_for_clickable(
                By.ID, "JobProfileFields.Folder_icimsDropdown"
            ).click()
            self.wait_for_clickable(
                By.XPATH, "//li[contains(text(), 'Closed (Not Filled)')]"
            ).click()
            self.wait_for_clickable(By.ID, "saveButton").click()
            self.switch_back_to_main_window()

        # Workflow execution
        self.logger(
            "class ICIMSAutomation:remove_old_postings",
            "Removing old job postings",
        )
        try:
            navigate_to_search_page()
            select_and_search_template(search_templates["first"])
            unpost_jobs()

            navigate_to_search_page()
            select_and_search_template(search_templates["second"])
            move_jobs_to_closed_no_fill()
            self.logger(
                "class ICIMSAutomation:remove_old_postings",
                "Old job postings removed",
            )
        except Exception as e:
            print(f"Exception during removing old postings: {str(e)}")
            self.logger(
                "class ICIMSAutomation:remove_old_postings",
                f"Error: {e}",
            )


def main():

    email = config("USERNAME")
    password = config("PASSWORD")
    cookies_path = config("COOKIES_PATH")
    job_template_id = config("JOB_TEMPLATE_ID")
    job_search_templates = {
        "first": config("FIRST_SEARCH_TEMPLATE"),
        "second": config("SECOND_SEARCH_TEMPLATE"),
    }

    automation = ICIMSAutomation(email, password, cookies_path)

    automation.login()
    automation.create_new_job(job_template_id)
    automation.remove_old_postings(job_search_templates, job_template_id)
    automation.close_driver()


if __name__ == "__main__":
    main()
