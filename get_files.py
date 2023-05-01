import os
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from config import BASE_URL
from config import DL_BASE_URL
from alive_progress import alive_bar


def get_download_link():
    try:
        response = requests.get(BASE_URL)
    except:
        raise Exception("Unable to get download link")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        h4_elements = soup.find_all("h4")
        for h4 in h4_elements:
            if h4.text.strip().startswith("export-fiches-rncp-v3"):
                last_export_fiches_rncp_v2_id = (
                    h4["id"].replace("resource-", "").replace("-title", "")
                )
                return DL_BASE_URL + last_export_fiches_rncp_v2_id
    else:
        raise Exception("Failed to get download link")


def download_file(url, file_path=os.getcwd() + "data.zip"):
    print("Downloading latest file...")
    try:
        response = requests.get(url, stream=True)

    except:
        raise Exception("Unable to download latest file")
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

    except:
        raise Exception("Unable to write to file")


def extract_file(file_path, folder_path=os.path.join(os.getcwd(), "app")):
    print("Extracting zip file")
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            assert len((zip_ref.namelist())) == 1
            zip_ref.extractall(folder_path)
            os.remove(file_path)

            return zip_ref.namelist()[0]
    except:
        raise Exception("Unable to extract file")


if __name__ == "__main__":
    link = get_download_link()

    download_file(link)
    name = extract_file(os.getcwd() + "data.zip")
    print(name)
