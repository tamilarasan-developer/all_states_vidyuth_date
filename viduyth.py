

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import os
import json

states = [
"andhra-pradesh","arunachal-pradesh","assam","bihar","chhattisgarh",
"goa","gujarat","haryana","himachal-pradesh","jharkhand",
"karnataka","kerala","madhya-pradesh","maharashtra","manipur",
"meghalaya","mizoram","nagaland","odisha","punjab",
"rajasthan","sikkim","tamil-nadu","telangana","tripura",
"uttar-pradesh","uttarakhand","west-bengal","delhi"
]

screenshot_folder = "screenshots"
output_folder = "output"

os.makedirs(screenshot_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.page_load_strategy = "eager"

# disable images (faster)
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

driver.set_window_size(1920,1080)

# smart wait
driver.implicitly_wait(5)

print("\nSTATE | TIME BLOCK | YESTERDAY | CURRENT")

results = {
    "time_block": "N/A",
    "states": {}
}

for state in states:

    try:

        url = f"https://vidyutpravah.in/state-data/{state}"

        driver.get(url)

        # stop extra loading
        driver.execute_script("window.stop();")

        screenshot_path=f"{screenshot_folder}/{state}.png"
        driver.save_screenshot(screenshot_path)

        soup=BeautifulSoup(driver.page_source,"html.parser")

        text=soup.get_text(" ")

        time_match=re.search(r"TIME BLOCK\s*([\d:]+\s*-\s*[\d:]+)",text)
        time_block=time_match.group(1) if time_match else "N/A"

        demand_section=re.search(
            r"State's Demand Met(.*?)Power Purchased",
            text,
            re.S
        )

        current="N/A"
        yesterday="N/A"

        if demand_section:

            block=demand_section.group(1)

            current_match=re.search(r"CURRENT\s*:\s*([\d,]+)",block)
            yesterday_match=re.search(r"YESTERDAY\s*:\s*([\d,]+)",block)

            if current_match:
                current=current_match.group(1)

            if yesterday_match:
                yesterday=yesterday_match.group(1)

        print(f"{state} | {time_block} | {yesterday} MW | {current} MW")

        if results["time_block"] == "N/A" and time_block != "N/A":
            results["time_block"] = time_block

        results["states"][state] = {
            "yesterday_demand_MW": yesterday,
            "current_demand_MW": current
        }

    except:
        print(f"{state} | ERROR")

driver.quit()

json_path=f"{output_folder}/demand_data.json"

with open(json_path,"w") as f:
    json.dump(results,f,indent=4)

print("\nData saved to:",json_path)




