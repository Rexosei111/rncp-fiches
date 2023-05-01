import re
from datetime import datetime

from alive_progress import alive_bar
from config import *
from data_model import *
from save_data import insert_in_db
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

settings = get_settings()


engine = create_engine(settings.db_url)

Session = sessionmaker(bind=engine)


def remove_none(item_dict: dict):
    return {key: value for key, value in item_dict.items() if value is not None}


def transform_fiche_dict(fiche):
    data = {
        "id_externe_fiche": fiche["ID_FICHE"],
        "numero_RNCP": fiche.get("NUMERO_FICHE"),
        "ancienne_certification": fiche.get("ANCIENNE_CERTIFICATION", None),
        "nouvelle_certification": fiche.get("NOUVELLE_CERTIFICATION", None),
        "intitule": fiche.get("INTITULE", None),
        "abrege_code": fiche.get("ABREGE", {}).get("CODE", None),
        "abrege_libelle": fiche.get("ABREGE", {}).get("LIBELLE", None),
        "etat_fiche": fiche.get("ETAT_FICHE", None),
        "nomenclature_europe_niveau": fiche.get("NOMENCLATURE_EUROPE", {}).get(
            "NIVEAU", None
        ),
        "nomenclature_europe_intitule": fiche.get("NOMENCLATURE_EUROPE", {}).get(
            "INTITULE", None
        ),
        "existence_partenaires": fiche.get("EXISTENCE_PARTENAIRES", None),
        "si_jury_fi": fiche.get("SI_JURY_FI", None),
        "si_jury_ca": fiche.get("SI_JURY_CA", None),
        "si_jury_fc": fiche.get("SI_JURY_FC", None),
        "si_jury_cq": fiche.get("SI_JURY_CQ", None),
        "si_jury_cl": fiche.get("SI_JURY_CL", None),
        "si_jury_vae": fiche.get("SI_JURY_VAE", None),
        "accessible_nouvelle_caledonie": fiche.get(
            "ACCESSIBLE_NOUVELLE_CALEDONIE", None
        ),
        "accessible_polynesie_francaise": fiche.get(
            "ACCESSIBLE_POLYNESIE_FRANCAISE", None
        ),
        "url_description": fiche.get("LIEN_URL_DESCRIPTION", None),
        "date_fin_enregistrement": fiche.get("DATE_FIN_ENREGISTREMENT", None),
        "date_effet": fiche.get("DATE_EFFET", None),
        "type_enregistrement": fiche.get("TYPE_ENREGISTREMENT", None),
        "statut": fiche.get("ACTIF", None),
        "duree_enregistrement": fiche.get("DUREE_ENREGISTREMENT", None),
        "date_dernier_jo": fiche.get("DATE_DERNIER_JO", None),
        "date_decision": fiche.get("DATE_DECISION", None),
    }
    return data


def transform_fiche_description_dict(fiche, update_fiche_id):
    return {
        "activites_visees": fiche.get("ACTIVITES_VISEES", None),
        "capacites_attestees": fiche.get("CAPACITES_ATTESTEES", None),
        "secteurs_activite": fiche.get("SECTEURS_ACTIVITE", None),
        "type_emploi_accessibles": fiche.get("TYPE_EMPLOI_ACCESSIBLES", None),
        "objectifs_contexte": fiche.get("OBJECTIFS_CONTEXTE", None),
        "reglementations_activites": fiche.get("REGLEMENTATIONS_ACTIVITES", None),
        "fiche_id": update_fiche_id,
        "prerequis_entree_formation_bloc": fiche.get(
            "PREREQUIS_ENTREE_FORMATION_BLOC", None
        ),
        "prerequis_validation_bloc": fiche.get("PREREQUIS_VALIDATION_BLOC", None),
    }


def transform_fiche_TextesReglementaires(fiche, update_fiche_id):
    pub_gen = None
    try:
        pub_gen = fiche["PUBLICATION_DECRET_GENERAL"]["PUBLICATION_JO"][
            "DATE_PUBLICATION_JO"
        ]
    except:
        pass
    return {
        "publication_decret_general": pub_gen,
        "publication_decret_creation": fiche.get("PUBLICATION_DECRET_CREATION", None),
        "publication_decret_autre": fiche.get("PUBLICATION_DECRET_AUTRE", None),
        "fiche_id": update_fiche_id,
    }


def transform_fiche_BlocsCompetences(bloc, update_fiche_id):
    return {
        "code_bloc": bloc.get("CODE", None),
        "libelle": bloc.get("LIBELLE", None),
        "liste_competences": remove_html_tags(bloc.get("LISTE_COMPETENCES", None)),
        "modalites_evaluation": remove_html_tags(
            bloc.get("MODALITES_EVALUATION", None)
        ),
        "fiche_id": update_fiche_id,
    }


def boolean_transformation(dictionary, key):
    """
    Pour un dictionnaire et une clé donnée, transforme la data oui/non en booléen
    """
    if key in dictionary:
        if dictionary[key] == "Oui":
            dictionary[key] = True
            return dictionary
        elif dictionary[key] == "Non":
            dictionary[key] = False
            return dictionary
        else:
            pass


def remove_html_tags(text):
    """Remove all HTML tags from a given string of text, except for <li> and <br> tags that are replaced by ' ; '."""
    if isinstance(text, str):
        clean = re.compile("<(?!li|br|/li|/br)[^>]*>")
        text = re.sub(clean, "", text)
        text = re.sub("<li>", ";", text)
        text = re.sub("<br>", ";", text)
        text = re.sub("</li>", "", text)
        text = re.sub("</br>", "", text)
        return text


def remove_html_tags_from_dict(dictionary, key):
    if key in dictionary:
        dictionary[key] = remove_html_tags(dictionary[key])
        return dictionary


def transform_str_to_date(dictionary, key):
    if key in dictionary:
        date_string = dictionary[key]
        date_format = "%d/%m/%Y"
        dictionary[key] = datetime.strptime(date_string, date_format)
        return dictionary


def extract_titles(dictionary, key):
    if key in dictionary:
        if "PUBLICATION_JO" in dictionary[key]:
            if isinstance(dictionary[key]["PUBLICATION_JO"], list):
                titles = [
                    remove_html_tags(sub_dict["TITRE"])
                    for sub_dict in dictionary[key]["PUBLICATION_JO"]
                ]
                separator = ", "
                titles = separator.join(titles)
            else:
                if (
                    dictionary[key]["PUBLICATION_JO"] is not None
                    and "TITRE" in dictionary[key]["PUBLICATION_JO"]
                ):
                    titles = remove_html_tags(
                        dictionary[key]["PUBLICATION_JO"]["TITRE"]
                    )
                else:
                    titles = None
            dictionary[key] = titles
            return dictionary


def extract_old_RNCP(dictionary):
    if "ANCIENNE_CERTIFICATION" in dictionary:
        if isinstance(dictionary["ANCIENNE_CERTIFICATION"], list):
            old_RNCP = dictionary["ANCIENNE_CERTIFICATION"]
            separator = ", "
            old_RNCP = separator.join(old_RNCP)
            dictionary["ANCIENNE_CERTIFICATION"] = old_RNCP
            return dictionary


def extract_new_RNCP(dictionary):
    if "NOUVELLE_CERTIFICATION" in dictionary:
        if isinstance(dictionary["NOUVELLE_CERTIFICATION"], list):
            new_RNCP = dictionary["NOUVELLE_CERTIFICATION"]
            separator = ", "
            new_RNCP = separator.join(new_RNCP)
            dictionary["NOUVELLE_CERTIFICATION"] = new_RNCP
            return dictionary


def update_db_data(final_dict):
    with alive_bar(len(final_dict)) as bar:
        for index, fiche in enumerate((change for change in final_dict)):
            session = Session()
            id_externe_fiche = fiche["ID_FICHE"]
            fiche_exist = session.query(Fiches).filter(
                Fiches.id_externe_fiche == id_externe_fiche
            )
            if not fiche_exist.count() > 0:
                insert_in_db([fiche])
                session.close()
                continue

            fiche_exist.update(remove_none(transform_fiche_dict(fiche)))

            updated_fiche = fiche_exist.one_or_none()

            updated_fiche_id = updated_fiche.id

            session.query(FichesDescriptions).filter(
                FichesDescriptions.fiche_id == updated_fiche_id
            ).update(
                remove_none(transform_fiche_description_dict(fiche, updated_fiche_id))
            )

            session.query(TextesReglementaires).filter(
                TextesReglementaires.fiche_id == updated_fiche_id
            ).update(
                remove_none(
                    transform_fiche_TextesReglementaires(fiche, updated_fiche_id)
                )
            )

            if "BLOCS_COMPETENCES" in fiche:
                if "BLOC_COMPETENCES" in fiche["BLOCS_COMPETENCES"]:
                    if isinstance(fiche["BLOCS_COMPETENCES"]["BLOC_COMPETENCES"], list):
                        for bloc in fiche["BLOCS_COMPETENCES"]["BLOC_COMPETENCES"]:
                            existing_bloc = session.query(BlocsCompetences).filter(
                                BlocsCompetences.code_bloc == bloc.get("CODE", None),
                                BlocsCompetences.fiche_id == updated_fiche_id,
                            )
                            if existing_bloc.count() > 0:
                                existing_bloc.update(
                                    remove_none(
                                        transform_fiche_BlocsCompetences(
                                            bloc, updated_fiche_id
                                        )
                                    )
                                )

                            new_bloc_competences = BlocsCompetences(
                                code_bloc=bloc.get("CODE", None),
                                libelle=bloc.get("LIBELLE", None),
                                liste_competences=bloc.get("LISTE_COMPETENCES", None),
                                modalites_evaluation=bloc.get(
                                    "MODALITES_EVALUATION", None
                                ),
                                fiche=updated_fiche,
                            )

                            session.add(new_bloc_competences)

            for key, value in fiche.items():
                if key.startswith("JURY_"):
                    existing_jury_description = session.query(JuryDescription).filter(
                        JuryDescription.jury_type == key,
                        JuryDescription.fiche_id == updated_fiche_id,
                    )
                    if existing_jury_description:
                        existing_jury_description.update(
                            remove_none(
                                {
                                    "jury_type": key,
                                    "jury_description": fiche.get(key),
                                    "fiche_id": updated_fiche_id,
                                }
                            )
                        )
                    else:
                        new_jury_description = JuryDescription(
                            jury_type=key,
                            jury_description=fiche.get(key),
                            fiche_id=updated_fiche_id,
                        )
                        session.add(new_jury_description)

            if "STATISTIQUES_PROMOTIONS" in fiche:
                if "STATISTIQUES_PROMOTION" in fiche["STATISTIQUES_PROMOTIONS"]:
                    if isinstance(
                        fiche["STATISTIQUES_PROMOTIONS"]["STATISTIQUES_PROMOTION"], list
                    ):
                        for stat in fiche["STATISTIQUES_PROMOTIONS"][
                            "STATISTIQUES_PROMOTION"
                        ]:
                            existing_statistiques_promotion = (
                                session.query(StatistiquesPromotion)
                                .filter(
                                    StatistiquesPromotion.annee == stat["ANNEE"],
                                )
                                .first()
                            )
                            if existing_statistiques_promotion:
                                existing_statistiques_promotion.update(
                                    remove_none(
                                        {
                                            "annee": stat.get("ANNEE", None),
                                            "nombre_certifies": stat.get(
                                                "NOMBRE_CERTIFIES", None
                                            ),
                                            "nombre_certifies_vae": stat.get(
                                                "NOMBRE_CERTIFIES_VAE", None
                                            ),
                                            "taux_insertion_global_6": stat.get(
                                                "TAUX_INSERTION_GLOBAL_6MOIS", None
                                            ),
                                            "taux_insertion_metier_24": stat.get(
                                                "TAUX_INSERTION_METIER_2ANS", None
                                            ),
                                            "fiche_id": updated_fiche_id,
                                        }
                                    )
                                )
                            else:
                                new_stat_prom = StatistiquesPromotion(
                                    annee=stat.get("ANNEE", None),
                                    nombre_certifies=stat.get("NOMBRE_CERTIFIES", None),
                                    nombre_certifies_vae=stat.get(
                                        "NOMBRE_CERTIFIES_VAE", None
                                    ),
                                    taux_insertion_global_6=stat.get(
                                        "TAUX_INSERTION_GLOBAL_6MOIS", None
                                    ),
                                    taux_insertion_metier_24=stat.get(
                                        "TAUX_INSERTION_METIER_2ANS", None
                                    ),
                                    fiche=updated_fiche,
                                )
                                session.add(new_stat_prom)

            # gestion des partenaires
            if "PARTENAIRES" in fiche:
                if "PARTENAIRE" in fiche["PARTENAIRES"]:
                    if isinstance(fiche["PARTENAIRES"]["PARTENAIRE"], list):
                        for partenaire in fiche["PARTENAIRES"]["PARTENAIRE"]:
                            siret_partenaire = partenaire.get(
                                "SIRET_PARTENAIRE", "Inconnu"
                            )
                            siret_exists = session.query(Organismes).filter(
                                Organismes.siret_organismes == siret_partenaire
                            )

                            if not siret_exists.count() > 0:
                                new_organismes = Organismes(
                                    siret_organismes=siret_partenaire,
                                    nom_organismes=partenaire.get(
                                        "NOM_PARTENAIRE", None
                                    ),
                                )

                                session.add(new_organismes)
                            else:
                                siret_exists.update(
                                    remove_none(
                                        {
                                            "siret_partenaire": siret_partenaire,
                                            "nom_partenaire": partenaire.get(
                                                "NOM_PARTENAIRE", None
                                            ),
                                        }
                                    )
                                )

                            new_organismes = siret_exists.first()

                            fiches_part = session.query(FichesPartenaires).filter(
                                FichesPartenaires.fiche_id == updated_fiche_id,
                                FichesPartenaires.organismes_id == new_organismes.id,
                            )

                            if not fiches_part.count() > 0:
                                new_fiche_partenaire = FichesPartenaires(
                                    fiche=updated_fiche,
                                    organismes=new_organismes,
                                    habilitation_partenaire=partenaire.get(
                                        "HABILITATION_PARTENAIRE", None
                                    ),
                                    etat_habilitation=partenaire.get(
                                        "ETAT_HABILITATION", None
                                    ),
                                    date_actif=partenaire.get("DATE_ACTIF", None),
                                    date_derniere_modification_etat=partenaire.get(
                                        "DATE_DERNIERE_MODIFICATION_ETAT", None
                                    ),
                                )
                                session.add(new_fiche_partenaire)
                            else:
                                fiches_part.update(
                                    remove_none(
                                        {
                                            "habilitation_partenaire": partenaire.get(
                                                "HABILITATION_PARTENAIRE", None
                                            ),
                                            "etat_habilitation": partenaire.get(
                                                "ETAT_HABILITATION", None
                                            ),
                                            "date_actif": partenaire.get(
                                                "DATE_ACTIF", None
                                            ),
                                            "date_derniere_modification_etat": partenaire.get(
                                                "DATE_DERNIERE_MODIFICATION_ETAT", None
                                            ),
                                        }
                                    )
                                )
            # Gestion des certificateurs

            if "CERTIFICATEURS" in fiche:
                if "CERTIFICATEUR" in fiche["CERTIFICATEURS"]:
                    if isinstance(fiche["CERTIFICATEURS"]["CERTIFICATEUR"], list):
                        for certificateur in fiche["CERTIFICATEURS"]["CERTIFICATEUR"]:
                            siret_certificateur = certificateur.get(
                                "SIRET_CERTIFICATEUR", "Inconnu"
                            )
                            siret_exists = session.query(Organismes).filter(
                                Organismes.siret_organismes == siret_certificateur
                            )

                            if not siret_exists.count() > 0:
                                new_organismes = Organismes(
                                    siret_organismes=siret_certificateur,
                                    nom_organismes=certificateur.get(
                                        "NOM_CERTIFICATEUR", None
                                    ),
                                )
                                session.add(new_organismes)
                                new_fiche_certificateur = FichesCertificateurs(
                                    fiche=updated_fiche, organismes=new_organismes
                                )

                                session.add(new_fiche_certificateur)

                            else:
                                siret_exists.update(
                                    remove_none(
                                        {
                                            "nom_certificateur": certificateur.get(
                                                "NOM_CERTIFICATEUR", None
                                            ),
                                        }
                                    )
                                )

                    else:
                        siret_certificateur = fiche["CERTIFICATEURS"][
                            "CERTIFICATEUR"
                        ].get("SIRET_CERTIFICATEUR", "Inconnu")
                        siret_exists = session.query(Organismes).filter(
                            Organismes.siret_organismes == siret_certificateur
                        )
                        if not siret_exists.count() > 0:
                            new_organismes = Organismes(
                                siret_organismes=siret_certificateur,
                                nom_organismes=fiche["CERTIFICATEURS"][
                                    "CERTIFICATEUR"
                                ].get("NOM_CERTIFICATEUR", None),
                            )
                            session.add(new_organismes)
                            new_fiche_certificateur = FichesCertificateurs(
                                fiche=updated_fiche, organismes=new_organismes
                            )

                            session.add(new_fiche_certificateur)

                        else:
                            siret_exists.update(
                                remove_none(
                                    {
                                        "nom_certificateur": fiche["CERTIFICATEURS"][
                                            "CERTIFICATEUR"
                                        ].get("NOM_CERTIFICATEUR", None)
                                    }
                                )
                            )
            # Gestion des codes NSF

            if "CODES_NSF" in fiche:
                if "NSF" in fiche["CODES_NSF"]:
                    if isinstance(fiche["CODES_NSF"]["NSF"], list):
                        for code_nsf in fiche["CODES_NSF"]["NSF"]:
                            code = code_nsf.get("CODE", "ICNU")
                            code_exists = session.query(CodesNSF).filter(
                                CodesNSF.code_nsf == code
                            )

                            if not code_exists.count() > 0:
                                new_code = CodesNSF(
                                    code_nsf=code,
                                    libelle=code_nsf.get("INTITULE", None),
                                )
                                session.add(new_code)
                                new_fiche_code = FichesCodesNSF(
                                    fiche=updated_fiche, code_NSF=new_code
                                )

                                session.add(new_fiche_code)
                            else:
                                new_code = code_exists.update(
                                    remove_none(
                                        {"libelle": code_nsf.get("INTITULE", None)}
                                    )
                                )

                    else:
                        code = fiche["CODES_NSF"]["NSF"].get("CODE", "ICNU")
                        code_exists = session.query(CodesNSF).filter(
                            CodesNSF.code_nsf == code
                        )

                        if not code_exists.count() > 0:
                            new_code = CodesNSF(
                                code_nsf=code,
                                libelle=fiche["CODES_NSF"]["NSF"].get("INTITULE", None),
                            )
                            session.add(new_code)
                            new_fiche_code = FichesCodesNSF(
                                fiche=updated_fiche, code_NSF=new_code
                            )
                            session.add(new_fiche_code)

                        else:
                            new_code = code_exists.update(
                                {"libelle": code.get("INTITULE", None)}
                            )

            # Codes ROME

            if "CODES_ROME" in fiche:
                if "ROME" in fiche["CODES_ROME"]:
                    if isinstance(fiche["CODES_ROME"]["ROME"], list):
                        for code_rome in fiche["CODES_ROME"]["ROME"]:
                            code = code_rome.get("CODE", "ICNU")
                            code_exists = session.query(CodesROME).filter(
                                CodesROME.code_rome == code
                            )

                            if not code_exists.count() > 0:
                                new_code = CodesROME(
                                    code_rome=code,
                                    libelle=code_rome.get("LIBELLE", None),
                                )
                                session.add(new_code)

                                session.flush()  # Flush the session to get the newly generated 'id'
                                code_rome_id = new_code.id
                                new_fiche_code = FichesCodesROME(
                                    fiche=updated_fiche, code_rome_id=code_rome_id
                                )

                                session.add(new_fiche_code)

                            else:
                                code_rome_id = code_exists.update(
                                    remove_none(
                                        {
                                            "code_rome": code,
                                            "libelle": code_rome.get("LIBELLE", None),
                                        }
                                    )
                                )

                    else:
                        code = fiche["CODES_ROME"]["ROME"].get("CODE", "ICNU")
                        code_exists = session.query(CodesROME).filter(
                            CodesROME.code_rome == code
                        )

                        if not code_exists.count() > 0:
                            new_code = CodesROME(
                                code_rome=code,
                                libelle=fiche["CODES_ROME"]["ROME"].get(
                                    "LIBELLE", None
                                ),
                            )
                            session.add(new_code)
                            session.flush()  # Flush the session to get the newly generated 'id'
                            code_rome_id = new_code.id
                            new_fiche_code = FichesCodesROME(
                                fiche=updated_fiche, code_rome_id=code_rome_id
                            )

                            session.add(new_fiche_code)

                        else:
                            code_rome_id = code_exists.update(
                                remove_none(
                                    {
                                        "code_rome": code,
                                        "libelle": fiche["CODES_ROME"]["ROME"].get(
                                            "LIBELLE", None
                                        ),
                                    }
                                )
                            )
            # Gestion des formacodes

            if "FORMACODES" in fiche:
                if "FORMACODE" in fiche["FORMACODES"]:
                    if isinstance(fiche["FORMACODES"]["FORMACODE"], list):
                        for code_formacode in fiche["FORMACODES"]["FORMACODE"]:
                            code = code_formacode.get("CODE", "ICNU")
                            code_exists = session.query(Formacodes).filter(
                                Formacodes.formacode == code
                            )

                            if not code_exists.count() > 0:
                                new_code = Formacodes(
                                    formacode=code,
                                    libelle=code_formacode.get("LIBELLE", None),
                                )
                                session.add(new_code)
                                new_fiche_code = FichesFormacodes(
                                    fiche=updated_fiche, formacodes=new_code
                                )

                                session.add(new_fiche_code)

                            else:
                                new_code = code_exists.update(
                                    remove_none(
                                        {
                                            "formacode": code,
                                            "libelle": code_formacode.get(
                                                "LIBELLE", None
                                            ),
                                        }
                                    )
                                )

                    else:
                        code = fiche["FORMACODES"]["FORMACODE"].get("CODE", "ICNU")
                        code_exists = session.query(Formacodes).filter(
                            Formacodes.formacode == code
                        )

                        if not code_exists.count() > 0:
                            new_code = Formacodes(
                                formacode=code,
                                libelle=fiche["FORMACODES"]["FORMACODE"].get(
                                    "LIBELLE", None
                                ),
                            )
                            session.add(new_code)
                            new_fiche_code = FichesFormacodes(
                                fiche=updated_fiche, formacodes=new_code
                            )

                            session.add(new_fiche_code)

                        else:
                            new_code = code_exists.update(
                                {
                                    "formacode": code,
                                    "libelle": code.get("LIBELLE", None),
                                }
                            )

            # Gestion des CCN

            for key, value in fiche.items():
                if key in ["CCN_1", "CCN_2", "CCN_3"]:
                    numero = fiche.get(key).get("NUMERO", "ICNU")
                    code_exists = session.query(CCN).filter(CCN.numero == numero)

                    if not code_exists.count() > 0:
                        new_ccn = CCN(
                            numero=fiche.get(key).get("NUMERO", "ICNU"),
                            libelle=fiche.get(key).get("LIBELLE", None),
                        )
                        session.add(new_ccn)
                        new_fiche_ccn = FichesCCN(
                            fiche=updated_fiche, ccn_related=new_ccn
                        )

                        session.add(new_fiche_ccn)

                    else:
                        new_ccn = code_exists.update(
                            remove_none(
                                {
                                    "numero": fiche.get(key).get("NUMERO", "ICNU"),
                                    "libelle": fiche.get(key).get("LIBELLE", None),
                                }
                            )
                        )

            # Gestion des IDCC

            if "CODES_IDCC" in fiche:
                if "IDCC" in fiche["CODES_IDCC"]:
                    if isinstance(fiche["CODES_IDCC"]["IDCC"], list):
                        for code_idcc in fiche["CODES_IDCC"]["IDCC"]:
                            code = code_idcc.get("CODE", "ICNU")
                            code_exists = session.query(IDCC).filter(
                                IDCC.code_idcc == code
                            )

                            if not code_exists.count() > 0:
                                new_code = IDCC(
                                    code_idcc=code,
                                    libelle=code_idcc.get("LIBELLE", None),
                                )
                                session.add(new_code)
                                new_fiche_code = FichesIDCC(
                                    fiche=updated_fiche, idcc=new_code
                                )

                                session.add(new_fiche_code)
                            else:
                                new_code = code_exists.update(
                                    remove_none(
                                        {
                                            "code_idcc": code,
                                            "libelle": code_idcc.get("LIBELLE", None),
                                        }
                                    )
                                )

                    else:
                        code = fiche["CODES_IDCC"]["IDCC"].get("CODE", "ICNU")
                        code_exists = session.query(IDCC).filter(IDCC.code_idcc == code)

                        if not code_exists.count() > 0:
                            new_code = IDCC(
                                code_idcc=code,
                                libelle=fiche["CODES_IDCC"]["IDCC"].get(
                                    "LIBELLE", None
                                ),
                            )
                            session.add(new_code)
                            new_fiche_code = FichesIDCC(
                                fiche=updated_fiche, idcc=new_code
                            )

                            session.add(new_fiche_code)
                        else:
                            new_code = code_exists.update(
                                remove_none(
                                    {
                                        "code_idcc": code,
                                        "libelle": fiche["CODES_IDCC"]["IDCC"].get(
                                            "LIBELLE", None
                                        ),
                                    }
                                )
                            )

            # Commit the changes to the database
            session.commit()
            session.close()
            bar()

        # Close the session
    print("over ok")
