import time
import re
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class EVDatabaseScraper:
    def __init__(self):

        self.base_url = "https://ev-database.org"
        self.data = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # comenta aquesta línia per veure el navegador
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")

        # Inicia el driver: webdriver-manager descarrega la versió adequada del chromedriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )


    def __accept_banner(self):
    #https://stackoverflow.com/questions/73093929/selenium-consent-to-cookie-pop-up
        try:

            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                "div.fc-consent-root button[aria-label='Consent'] p.fc-button-label"))).click()

            time.sleep(2)

        except Exception:
            return

    def __set_items_per_page(self):

        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-type='items-per-page-dd']"))
            )

            dropdown_panel = self.driver.find_element(By.CSS_SELECTOR,
                                                      "div[data-type='items-per-page-dd'] div[data-type='panel']")
            dropdown_panel.click()
            time.sleep(1)

            option_50 = self.driver.find_element(By.CSS_SELECTOR,
                                                 "div[data-type='items-per-page-dd'] div[data-value='50']")
            option_50.click()

            time.sleep(2)  

        except Exception as e:
            print(f"⚠️ No s'ha pogut seleccionar '50 per page': {e}")

    def __download_html(self, url: str):

        self.driver.get(url)
        page_source = self.driver.page_source
        return page_source


    def __get_vehicle_links(self, html: str, limit_pages=None) -> list:

        links_set = set()
        page_count = 0

        #self.driver.find_element(By.CSS_SELECTOR, "button[data-type='next']").click()

        while True:
            soup = BeautifulSoup(html, "html.parser")
            anchors = soup.findAll('a', href=True)

            for a in anchors:
                href = a.get("href")
                if href and "/car/" in href:
                    links_set.add(self.base_url + href)

            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-type='next']")
                # Si està desactivat (classe jplist-disabled), sortim
                if "jplist-disabled" in next_button.get_attribute("class"):
                    print("✅ Última pàgina trobada.")
                    break

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                # Si no està desactivat, fem clic per anar a la següent
                next_button.click()
                time.sleep(2)  # espera que carregui la següent pàgina

                # ✅ Actualitzem el HTML per analitzar la nova pàgina
                html = self.driver.page_source

            except Exception:
                # Si el botó no existeix o falla, parem
                print("⚠️ No s'ha pogut trobar o clicar el botó 'next'. Finalitzant la cerca.")
                break

            page_count += 1
            if page_count >= limit_pages:
                print("Límit de pàgines assolit")
                break

        links = list(links_set)
        return links

    def __scrape_vehicle_data(self, html: str) -> None:
        if "Request blocked" in html or "anomalies detected" in html:
            print("⚠️ Pàgina bloquejada detectada, s'omet.")
            return

        soup = BeautifulSoup(html, "html.parser")

        features = ['Brand', 'Model']
        example_data = []

        title_elem = soup.select_one("h1")
        if not title_elem:
            return
        model_name = title_elem.get_text(strip=True)
        brand = model_name.split()[0] if " " in model_name else model_name

        example_data.append(brand)
        example_data.append(model_name)


        allowed_sections = [
            "Price",
            "Available to Order",
            "Battery",
            "Charging",
            "Performance",
            "Energy Consumption",
            "Dimensions and Weight",
            "Miscellaneous"
        ]

        target_country = "Germany"

        # Busquem tots els divs de data-table dins la secció principal
        main_data_section = soup.select_one("section#main-data")
        if not main_data_section:
            # si no hi ha secció, només guardem brand/model
            if len(self.data) == 0:
                self.data.append(features)
            self.data.append(example_data)
            return

        # Iterem pels blocs data-table (cada bloc té un <h2> i una <table>)
        data_tables = main_data_section.select("div.data-table, div.inline-block")
        for block in data_tables:
            h2 = block.find("h2")
            if not h2:
                continue
            section_title = h2.get_text(strip=True)
            if section_title not in allowed_sections:
                continue

            table = block.find("table")
            if not table:
                continue

            value = ""

            # --- SECCIÓ PRICE ---
            if section_title == "Price":
                if len(self.data) == 0:
                    features.append("Price")

                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) < 2:
                        continue
                    country = tds[0].get_text(strip=True)
                    price_val = tds[1].get_text(strip=True)
                    if target_country.lower() in country.lower():
                        value = price_val
                        break

            # --- SECCIÓ AVAILABLE TO ORDER ---
            elif section_title == "Available to Order":
                if len(self.data) == 0:
                    features.append("Availability")

                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) < 2:
                        continue
                    country = tds[0].get_text(strip=True)
                    date_val = tds[1].get_text(strip=True)
                    if target_country.lower() in country.lower():
                        value = date_val
                        break

            # --- SECCIÓ BATTERY ---
            elif section_title == "Battery":
                if len(self.data) == 0:
                    features.append("Useable Battery")

                tables = block.find_all("table")
                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if "Useable Capacity" in label:
                            value = val
                            break
                    if value:  # si ja l’hem trobat, no cal seguir amb altres taules
                        break

            # --- SECCIÓ CHARGING ---
            elif section_title == "Charging":
                if len(self.data) == 0:
                    features.append("Charge Speed")

                tables = block.find_all("table")
                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if "Charge Speed" in label:
                            value = val
                            break
                    if value:  # si ja l’hem trobat, no cal seguir amb altres taules
                        break

            # --- SECCIÓ PERFORMANCE ---
            elif section_title == "Performance":
                if len(self.data) == 0:
                    features.append("Acceleration 0 - 100 km/h")
                    features.append("Top Speed")
                    features.append("Total Power")
                    features.append("Electric Range")

                tables = block.find_all("table")

                # Inicialitzem els valors buits
                acceleration_val = ""
                top_speed_val = ""
                total_power_val = ""
                electric_range = ""

                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if "Acceleration 0 - 100 km/h" in label:
                            acceleration_val = val
                        elif "Top Speed" in label:
                            top_speed_val = val
                        elif "Total Power" in label:
                            total_power_val = val
                        elif re.search(r"^Electric Range\s*\*?", label):
                            electric_range = val

            # --- SECCIÓ ENERGY CONSUMPTION ---
            elif section_title == "Energy Consumption":
                if len(self.data) == 0:
                    features.append("Vehicle Consumption")

                tables = block.find_all("table")
                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if re.search(r"^Vehicle Consumption\s*\*?", label):
                            value = val
                            break
                    if value:  # si ja l’hem trobat, no cal seguir amb altres taules
                        break

            # --- SECCIÓ DIMENSIONS AND WEIGHT ---
            elif section_title == "Dimensions and Weight":
                if len(self.data) == 0:
                    features.append("Length")
                    features.append("Width")
                    features.append("Height")
                    features.append("Cargo Volume")
                    features.append("Towing Weight Braked")

                tables = block.find_all("table")

                # Inicialitzem els valors buits
                length_val = ""
                width_val = ""
                height_val = ""
                cargo_range = ""
                towing_val = ""

                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if "Length" in label:
                            length_val = val
                        elif "Width" in label:
                            width_val = val
                        elif "Height" in label:
                            height_val = val
                        elif "Cargo Volume" in label:
                            cargo_range = val
                        elif "Towing Weight Braked" in label:
                            towing_val = val

            # --- SECCIÓ MISCELLANEOUS ---
            elif section_title == "Miscellaneous":
                if len(self.data) == 0:
                    features.append("Seats")

                tables = block.find_all("table")
                for table in tables:
                    trs = table.find_all("tr")
                    for tr in trs:
                        tds = tr.find_all("td")
                        if len(tds) < 2:
                            continue
                        label = tds[0].get_text(strip=True)
                        val = tds[1].get_text(strip=True)
                        if "Seats" in label:
                            value = val
                            break
                    if value:  # si ja l’hem trobat, no cal seguir amb altres taules
                        break


            if section_title == "Performance":
                example_data.append(acceleration_val)
                example_data.append(top_speed_val)
                example_data.append(total_power_val)
                example_data.append(electric_range)
            elif section_title == "Dimensions and Weight":
                example_data.append(length_val)
                example_data.append(width_val)
                example_data.append(height_val)
                example_data.append(cargo_range)
                example_data.append(towing_val)
            else:
                example_data.append(value)

        if len(self.data) == 0:
            self.data.append(features)
        self.data.append(example_data)

    def scrape(self, limit=None):

        print("🔍 Iniciant el web scraping d'EV Database...\n")
        start_html = self.__download_html(self.base_url)
        self.__accept_banner()
        time.sleep(3)
        self.__set_items_per_page()
        time.sleep(3)
        updated_html = self.driver.page_source
        vehicle_links = self.__get_vehicle_links(updated_html, limit_pages=1)


        for i, link in enumerate(vehicle_links):
            if limit is not None and i >= limit:
                print(f"✅ Límit de vehicles assolit ({limit})")
                break

            html = self.__download_html(link)
            self.__scrape_vehicle_data(html)
            # Espera aleatòria per no saturar el servidor
            time.sleep(random.uniform(1.5, 3))


        for link in vehicle_links:
            html = self.__download_html(link)
            self.__scrape_vehicle_data(html)
            # Espera aleatòria per no saturar el servidor
            time.sleep(random.uniform(1.5, 3))

        # Tancar el navegador quan acabi
        self.driver.quit()
        print("✅ Procés completat. Navegador tancat.")

    def data2csv(self, filename: str):
        """Exporta la llista de diccionaris a CSV."""
        if not self.data:
            print("⚠️ No hi ha dades per exportar.")
            return
        with open(filename, "w", encoding="utf-8") as file:
            for i in range(len(self.data)):
                for j in range(len(self.data[i])):
                    # Escriu el valor seguit d'un punt i coma
                    file.write(str(self.data[i][j]).strip() + ";")
                # Passa a la línia següent després de cada fila
                file.write("\n")

        print(f"💾 Dataset desat correctament a: {filename}")