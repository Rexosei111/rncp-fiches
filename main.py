import datetime
import json
import os

import xmltodict  # must be installed
from alive_progress import alive_bar
from get_files import download_file
from get_files import extract_file
from get_files import get_download_link
from save_data import boolean_transformation
from save_data import extract_new_RNCP
from save_data import extract_old_RNCP
from save_data import extract_titles
from save_data import remove_html_tags_from_dict
from save_data import transform_str_to_date
from update_data import update_db_data


def xml_to_dict(xml_file_path):
    with open(xml_file_path, "r") as f:
        xml_content = f.read()
        print(f"Parssing {os.path.basename(xml_file_path).split('/')[-1]}...")
        parse_content = xmltodict.parse(xml_content)
        return parse_content


def extract_fiches(xml_dict):
    print(f"Extracting Fiches list...")
    return xml_dict["FICHES"]["FICHE"]


codes = {
    "BLOC_COMPETENCES": "CODE",
    "PARTENAIRE": "SIRET_PARTENAIRE",
    "CERTIFICATEUR": "SIRET_CERTIFICATEUR",
    "NSF": "CODE",
    "ROME": "CODE",
    "FORMACODE": "CODE",
    "CN_1": "NUMERO",
    "CN_2": "NUMERO",
    "CN_3": "NUMERO",
    "IDCC": "CODE",
    "STATISTIQUES_PROMOTION": "ANNEE",
}


def transform_fiches(fiches):
    print("Transforming fiches")
    for index, fiche in enumerate(fiches):
        boolean_transformation(fiche, "EXISTENCE_PARTENAIRES")
        boolean_transformation(fiche, "SI_JURY_FI")
        boolean_transformation(fiche, "SI_JURY_CA")
        boolean_transformation(fiche, "SI_JURY_FC")
        boolean_transformation(fiche, "SI_JURY_CQ")
        boolean_transformation(fiche, "SI_JURY_CL")
        boolean_transformation(fiche, "SI_JURY_VAE")
        boolean_transformation(fiche, "ACCESSIBLE_NOUVELLE_CALEDONIE")
        boolean_transformation(fiche, "ACCESSIBLE_POLYNESIE_FRANCAISE")
        boolean_transformation(fiche, "ACTIF")
        remove_html_tags_from_dict(fiche, "LIEN_URL_DESCRIPTION")
        transform_str_to_date(fiche, "DATE_FIN_ENREGISTREMENT")
        transform_str_to_date(fiche, "DATE_EFFET")
        transform_str_to_date(fiche, "DATE_DERNIER_JO")
        transform_str_to_date(fiche, "DATE_DECISION")
        """
        remove_html_tags_from_dict(fiche, "ACTIVITES_VISEES")
        remove_html_tags_from_dict(fiche, "CAPACITES_ATTESTEES")
        remove_html_tags_from_dict(fiche, "SECTEURS_ACTIVITE")
        remove_html_tags_from_dict(fiche, "TYPE_EMPLOI_ACCESSIBLES")
        remove_html_tags_from_dict(fiche, "OBJECTIFS_CONTEXTE")
        remove_html_tags_from_dict(fiche, "REGLEMENTATIONS_ACTIVITES")
        """
        extract_titles(fiche, "PUBLICATION_DECRET_GENERAL")
        extract_titles(fiche, "PUBLICATION_DECRET_CREATION")
        extract_titles(fiche, "PUBLICATION_DECRET_AUTRE")
        extract_old_RNCP(fiche)
        extract_new_RNCP(fiche)


def get_change(dict_1, dict_2):
    change = {}
    for key, value in dict_1.items():
        if key not in dict_2:
            change[key] = value
        elif isinstance(value, dict) and isinstance(dict_2[key], dict):
            nested_change = get_change(value, dict_2[key])
            if bool(nested_change):
                change[key] = nested_change
        elif isinstance(value, list) and isinstance(dict_2[key], list):
            nested_changes = []
            if all(isinstance(element, str) for element in value) and all(
                isinstance(ele, str) for ele in dict_2[key]
            ):
                changed_list_items = [item for item in value if item not in dict_2[key]]
                if changed_list_items:
                    nested_changes.append({key: changed_list_items})
            else:
                unique_code = codes.get(key)
                for item in value:
                    old_gen_list = [
                        old_item
                        for old_item in dict_2[key]
                        if old_item.get(unique_code) == item.get(unique_code)
                    ]
                    try:
                        if not len(old_gen_list) > 0:
                            nested_changes.append(item)
                        else:
                            old_item = old_gen_list[0]
                            nchange = get_change(item, old_item)
                            if bool(nchange):
                                nested_changes.append(
                                    {**nchange, unique_code: item[unique_code]}
                                )
                    except:
                        ...
            if nested_changes:
                change[key] = nested_changes
        elif dict_2[key] != value:
            change[key] = value
    return change


def get_fiches_changes(new_fiches_list, old_fiches_list):
    print("Getting changes...")
    with alive_bar(len(new_fiches_list)) as bar:
        changes = []
        for index, fiche in enumerate(new_fiches_list):
            old_fiche = [
                old_fiche
                for old_fiche in old_fiches_list
                if old_fiche["ID_FICHE"] == fiche["ID_FICHE"]
            ]
            try:
                if not old_fiche:
                    changes.append(fiche)
                else:
                    old_fiche_data = old_fiche[0]
                    change = get_change(fiche, old_fiche_data)
                    if bool(change):
                        changes.append({**change, "ID_FICHE": fiche.get("ID_FICHE")})
            except:
                ...
            bar()
    print(f"{len(changes)} changes detected")
    with open(os.path.join(os.getcwd(), "changes.json"), "w") as f:
        f.write(json.dumps(changes, default=str))

    return changes


if __name__ == "__main__":
    print("\n", datetime.datetime.now())
    root_folder = os.getcwd()
    download_link = get_download_link()
    download_file(download_link, os.path.join(root_folder, "data.zip"))
    file_name = extract_file(os.path.join(root_folder, "data.zip"), root_folder)
    new_fiches_dict = xml_to_dict(file_name)
    new_fiches_list = extract_fiches(new_fiches_dict)
    old_fiches_list = []
    try:
        with open(os.path.join(root_folder, "old_fiches.json"), "r") as f:
            old_fiches_list = json.loads(f.read())
    except:
        old_fiches_list = []
    with open(os.path.join(root_folder, "old_fiches.json"), "w") as f:
        f.write(json.dumps(new_fiches_list))

    transform_fiches((fiche for fiche in new_fiches_list))
    transform_fiches((fiche for fiche in old_fiches_list))
    changes = get_fiches_changes(new_fiches_list, old_fiches_list)

    if len(changes) > 0:
        update_db_data(changes)
