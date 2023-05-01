import datetime
import json
import os

from get_files import download_file, extract_file, get_download_link
from main import extract_fiches, transform_fiches, xml_to_dict
from save_data import insert_in_db

if __name__ == "__main__":
    print("\n", datetime.datetime.now())
    root_folder = os.getcwd()
    download_link = get_download_link()
    download_file(download_link, os.path.join(root_folder, "data.zip"))
    file_name = extract_file(os.path.join(root_folder, "data.zip"), root_folder)
    new_fiches_dict = xml_to_dict(
        os.path.join(root_folder, "export_fiches_RNCP_V3_0_2023-04-30.xml")
    )
    new_fiches_list = extract_fiches(new_fiches_dict)
    # with open(os.path.join(root_folder, "old_fiches.json"), "r") as file:
    #     new_fiches_list = json.loads(file.read())
    with open(os.path.join(root_folder, "old_fiches.json"), "w") as f:
        f.write(json.dumps(new_fiches_list))
    print("\n\n")
    print("Populating Database...")
    insert_in_db(new_fiches_list)
    print("\nDatabase Population completed")
