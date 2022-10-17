from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options


@dataclass
class Credentials:
    """
    максимально небезопасно хранить
    логин и пароль в коде
    """

    username: str = ""
    password: str = ""
    domain: str = ""


class CallsParser:

    """
    парсер страницы контакт центр
    https://p1.cloudpbx.rt.ru/callcenter/reports/
    """

    def __init__(
        self,
        date_number: int,
        credentials: Credentials,
        path_to_driver: str = "./geckodriver.exe",
    ) -> None:
        assert date_number in range(1, 32), "Неверный день месяца"
        assert credentials.username, "Не указан логин"
        assert credentials.password, "Не указан пароль"

        self.date_number = date_number
        self.path_to_driver = path_to_driver

        self.service = Service(self.path_to_driver)
        driver_options = Options()
        self.driver = webdriver.Firefox(
            service=self.service,
            options=driver_options,
        )
        self.initial_web_page = "https://cloudpbx.rt.ru/callcenter/reports/"
        self.credentials = credentials

    def parse(self) -> None:
        self.driver.get(self.initial_web_page)

        username = self.driver.find_element(
            by=By.ID,
            value="username",
        )
        password = self.driver.find_element(
            by=By.ID,
            value="password",
        )
        domain = self.driver.find_element(
            by=By.ID,
            value="domain",
        )

        signin_button = self.driver.find_element(
            by=By.CLASS_NAME,
            value="btn.btn-lg.orange.mb-3.waves-effect.waves-light",
        )

        username.send_keys(self.credentials.username)
        password.send_keys(self.credentials.password)
        domain.send_keys(self.credentials.domain)
        signin_button.click()

        WebDriverWait(self.driver, timeout=30).until(
            lambda d: d.find_element(
                by=By.XPATH,
                value="//a[@href='/callcenter/']",
            ),
        )

        item_1 = self.driver.find_element(
            by=By.XPATH,
            value="//a[@href='/callcenter/']",
        )

        item_1.click()

        item_2 = self.driver.find_element(
            by=By.XPATH,
            value="//a[@href='/callcenter/reports/']",
        )
        item_2.click()

        WebDriverWait(self.driver, timeout=30).until(
            lambda d: d.find_element(
                by=By.XPATH,
                value="//select[@name='report_type_id']",
            ),
        )

        item_3 = self.driver.find_element(
            by=By.XPATH,
            value="//select[@name='report_type_id']",
        )
        item_3.click()

        item_4 = item_3.find_element(
            by=By.XPATH,
            value="//option[@value='7']",
        )

        item_4.click()

        WebDriverWait(self.driver, timeout=10).until(
            lambda d: d.find_element(
                by=By.CLASS_NAME,
                value="ui-datepicker-trigger",
            )
        )

        self.driver.execute_script(
            "document.querySelector('.ui-datepicker-trigger').click();"
        )

        TARGET_DATE = 12

        self.driver.execute_script(
            f"""
            let _$ = (selector) => document.querySelector(selector);
            let _$$ = (selector) => document.querySelectorAll(selector);
            
            _$('.ui-datepicker-calendar')
            .querySelectorAll(".ui-state-default")[{TARGET_DATE - 1}]
            .click();
            _$(".ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all").click();
            
            _$$('.ui-datepicker-trigger')[1].click();
            _$('.ui-datepicker-calendar')
            .querySelectorAll(".ui-state-default")[{TARGET_DATE - 1}].click();
            """
        )

        slider_1 = self.driver.find_element(
            by=By.ID,
            value="hourSlider",
        )
        slider_2 = self.driver.find_element(
            by=By.ID,
            value="minuteSlider",
        )
        button_1 = slider_1.find_element(
            by=By.CLASS_NAME,
            value="ui-slider-handle.ui-corner-all.ui-state-default",
        )
        action_1 = webdriver.ActionChains(self.driver)
        action_1.move_to_element(slider_1).click().perform()
        action_1.move_to_element(slider_1).click_and_hold(button_1).move_by_offset(
            0, -slider_1.size["height"] / 2
        ).click().perform()

        button_2 = slider_2.find_element(
            by=By.CLASS_NAME,
            value="ui-slider-handle.ui-corner-all.ui-state-default",
        )
        action_2 = webdriver.ActionChains(self.driver)
        action_2.move_to_element(slider_2).click().perform()
        action_2.move_to_element(slider_2).click_and_hold(button_2).move_by_offset(
            0, -slider_2.size["height"] / 2
        ).click().perform()

        close_button = self.driver.find_element(
            by=By.CLASS_NAME,
            value="ui-datepicker-close.ui-state-default.ui-priority-primary.ui-corner-all",
        )

        close_button.click()

        download_button = self.driver.find_element(
            by=By.CLASS_NAME,
            value="save",
        )

        download_button.click()
        self.driver.close()  # close the current window


if __name__ == "__main__":
    credentials = Credentials(
        username="",
        password="",
        domain="",
    )
    parser = CallsParser(date_number=12, credentials=credentials)
    parser.parse()
