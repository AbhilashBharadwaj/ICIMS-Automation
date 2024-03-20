import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from decouple import config

module = config("MODULE")
jerseySTEMUtilsLoggerURL = config("LOGGER")


class Scraper:
    # Default base URL and other constants for the scraper
    BASE_URL = config("URL")  # Default base URL, loaded from configuration
    WINDOW_SIZE = "1920x1080"  # Size of the browser window to use
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"  # User agent string for the browser

    def __init__(self, base_url=None):
        """
        Initializes the Scraper object, optionally with a custom base URL.
        
        :param base_url: Optional; The base URL for web scraping if you want to override the default.
        """
        if base_url:
            self.BASE_URL = base_url
        self.driver = self.setup_driver()

    def logger(self, function_name, message):
        """
        Logs messages to a remote logging service.

        :param function_name: Name of the function where the log is coming from.
        :param message: The log message.
        """
        requests.post(
            jerseySTEMUtilsLoggerURL,
            json={
                "module": module,
                "function_name": function_name,
                "message": message,
            },
        )

    def setup_driver(self):
        """
        Sets up the Selenium WebDriver with custom options.

        :return: Configured Selenium WebDriver.
        """
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment to run Chrome in headless mode.
        chrome_options.add_argument(f"--window-size={self.WINDOW_SIZE}")
        chrome_options.add_argument(f"user-agent={self.USER_AGENT}")
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver

    def navigate(self, endpoint=""):
        """
        Navigates to a specified endpoint relative to the BASE_URL.

        :param endpoint: The relative URL to navigate to. Defaults to an empty string, which navigates to the BASE_URL.
        """
        self.driver.get(f"{self.BASE_URL}/{endpoint}")

    def wait_for_element(self, locator_type, locator, timeout=10):
        """
        Waits for a specific element to be visible on the web page.

        :param locator_type: The type of the locator (e.g., By.ID, By.XPATH).
        :param locator: The locator string.
        :param timeout: Time in seconds to wait before throwing a timeout exception. Defaults to 10 seconds.
        :return: The WebElement found.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((locator_type, locator))
        )

    def wait_for_clickable(self, locator_type, locator, timeout=10):
        """
        Waits for a specific element to be clickable on the web page.

        :param locator_type: The type of the locator (e.g., By.ID, By.XPATH).
        :param locator: The locator string.
        :param timeout: Time in seconds to wait before throwing a timeout exception. Defaults to 10 seconds.
        :return: The WebElement found.
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((locator_type, locator))
        )

    def switch_to_frame(self, frame_id):
        """
        Switches the context to a specified iframe by its ID.

        :param frame_id: The ID of the iframe to switch to.
        """
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(frame_id)
        )

    def switch_to_new_window(self):
        """
        Switches the driver context to a new browser window that was opened.
        """
        self.original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.window_handles) > 1
        )
        new_window = [
            window
            for window in self.driver.window_handles
            if window != self.original_window
        ][-1]
        self.driver.switch_to.window(new_window)

    def switch_back_to_main_window(self):
        """
        Switches the driver context back to the original main window.
        """
        self.driver.switch_to.window(self.original_window)

    def close_driver(self):
        """
        Closes the browser and quits the driver.
        """
        self.driver.quit()