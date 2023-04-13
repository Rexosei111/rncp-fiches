from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.types import TypeDecorator


class DateFormat(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = datetime.strptime(value, "%d/%m/%Y")
        return value


Base = declarative_base()


class Fiches(Base):
    __tablename__ = "fiches"
    id = Column(Integer, primary_key=True)
    id_externe_fiche = Column(Integer, unique=True)
    numero_RNCP = Column(String(100), unique=True, index=True)
    ancienne_certification = Column(String(150))
    nouvelle_certification = Column(String(500))
    intitule = Column(String(700))
    abrege_code = Column(String(50))
    abrege_libelle = Column(String(100))
    etat_fiche = Column(String(70))
    nomenclature_europe_niveau = Column(String(10))
    nomenclature_europe_intitule = Column(String(120))
    existence_partenaires = Column(Boolean)
    si_jury_fi = Column(Boolean)
    si_jury_ca = Column(Boolean)
    si_jury_fc = Column(Boolean)
    si_jury_cq = Column(Boolean)
    si_jury_cl = Column(Boolean)
    si_jury_vae = Column(Boolean)
    accessible_nouvelle_caledonie = Column(Boolean)
    accessible_polynesie_francaise = Column(Boolean)
    url_description = Column(Text)
    date_fin_enregistrement = Column(DateFormat)
    date_effet = Column(DateFormat)
    type_enregistrement = Column(Text)
    statut = Column(Boolean)
    duree_enregistrement = Column(Integer)
    date_dernier_jo = Column(DateFormat)
    date_decision = Column(DateFormat)
    date_publication = Column(DateFormat)
    date_limite_delivrance = Column(DateFormat)
    prerequis_entree_formation = Column(Text)
    prerequis_validation_certification = Column(Text)

    fiches_partenaires = relationship(
        "FichesPartenaires", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_certificateurs = relationship(
        "FichesCertificateurs", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_codes_nsf = relationship(
        "FichesCodesNSF", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_codes_rome = relationship(
        "FichesCodesROME", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_formacodes = relationship(
        "FichesFormacodes", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_ccn = relationship(
        "FichesCCN", back_populates="fiche", cascade="all, delete-orphan"
    )
    fiches_idcc = relationship(
        "FichesIDCC", back_populates="fiche", cascade="all, delete-orphan"
    )

    # Define relationship for child tables
    fiches_descriptions = relationship(
        "FichesDescriptions",
        uselist=False,
        back_populates="fiche",
        cascade="all, delete-orphan",
    )
    textes_reglementaires = relationship(
        "TextesReglementaires",
        uselist=False,
        back_populates="fiche",
        cascade="all, delete-orphan",
    )
    blocs_competences = relationship(
        "BlocsCompetences", back_populates="fiche", cascade="all, delete-orphan"
    )
    jurys_descriptions = relationship(
        "JuryDescription", back_populates="fiche", cascade="all, delete-orphan"
    )
    statistiques_promotion = relationship(
        "StatistiquesPromotion", back_populates="fiche", cascade="all, delete-orphan"
    )

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesDescriptions(Base):
    __tablename__ = "fiches_descriptions"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    activites_visees = Column(Text)
    capacites_attestees = Column(Text)
    secteurs_activite = Column(Text)
    type_emploi_accessibles = Column(Text)
    objectifs_contexte = Column(Text)
    reglementations_activites = Column(Text)
    prerequis_entree_formation_bloc = Column(Text)
    prerequis_validation_bloc = Column(Text)
    fiche = relationship("Fiches", back_populates="fiches_descriptions")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TextesReglementaires(Base):
    __tablename__ = "textes_reglementaires"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    publication_decret_general = Column(Text)
    publication_decret_creation = Column(Text)
    publication_decret_autre = Column(Text)

    fiche = relationship("Fiches", back_populates="textes_reglementaires")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BlocsCompetences(Base):
    __tablename__ = "blocs_competences"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    code_bloc = Column(Text)
    libelle = Column(Text)
    liste_competences = Column(Text)
    modalites_evaluation = Column(Text)

    fiche = relationship("Fiches", back_populates="blocs_competences")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class JuryDescription(Base):
    __tablename__ = "jurys_descriptions"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    jury_type = Column(Text)
    jury_description = Column(Text)
    fiche = relationship("Fiches", back_populates="jurys_descriptions")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StatistiquesPromotion(Base):
    __tablename__ = "statistiques_promotion"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    annee = Column(Integer)
    nombre_certifies = Column(Integer)
    nombre_certifies_vae = Column(Integer)
    taux_insertion_global_6 = Column(Integer)
    taux_insertion_metier_24 = Column(Integer)
    fiche = relationship("Fiches", back_populates="statistiques_promotion")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Partenaires(Base):
    __tablename__ = "partenaires"
    id = Column(Integer, primary_key=True)
    siret_partenaire = Column(Text)
    nom_partenaire = Column(Text)
    # I deleted here
    fiches_partenaires = relationship("FichesPartenaires", back_populates="partenaire")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Certificateurs(Base):
    __tablename__ = "certificateurs"
    id = Column(Integer, primary_key=True)
    siret_certificateur = Column(Text)
    nom_certificateur = Column(Text)
    fiches_certificateurs = relationship(
        "FichesCertificateurs", back_populates="certificateur"
    )

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodesNSF(Base):
    __tablename__ = "codes_NSF"
    id = Column(Integer, primary_key=True)
    code_nsf = Column(String(20))
    libelle = Column(Text)
    fiches_codes_NSF = relationship("FichesCodesNSF", back_populates="code_NSF")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodesROME(Base):
    __tablename__ = "codes_rome"
    id = Column(Integer, primary_key=True)
    code_rome = Column(String(20))
    libelle = Column(Text)
    fiches_codes_rome = relationship("FichesCodesROME", back_populates="codes_rome")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Formacodes(Base):
    __tablename__ = "formacodes"
    id = Column(Integer, primary_key=True)
    formacode = Column(Integer)
    libelle = Column(Text)
    fiches_formacodes = relationship("FichesFormacodes", back_populates="formacodes")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IDCC(Base):
    __tablename__ = "idcc"
    id = Column(Integer, primary_key=True)
    code_idcc = Column(Integer)
    libelle = Column(Text)
    fiches_idcc = relationship("FichesIDCC", back_populates="idcc")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CCN(Base):
    __tablename__ = "ccn"
    id = Column(Integer, primary_key=True)
    numero = Column(Text)
    libelle = Column(Text)
    fiches_ccn = relationship("FichesCCN", back_populates="ccn_related")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesPartenaires(Base):
    __tablename__ = "fiches_partenaires"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    partenaire_id = Column(Integer, ForeignKey("partenaires.id"))

    # I made the changes here
    habilitation_partenaire = Column(Text)
    etat_habilitation = Column(Text)
    date_actif = Column(DateFormat)
    date_derniere_modification_etat = Column(DateFormat)

    fiche = relationship("Fiches", back_populates="fiches_partenaires")
    partenaire = relationship("Partenaires", back_populates="fiches_partenaires")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesCertificateurs(Base):
    __tablename__ = "fiches_certificateurs"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    certificateur_id = Column(Integer, ForeignKey("certificateurs.id"))
    fiche = relationship("Fiches", back_populates="fiches_certificateurs")
    certificateur = relationship(
        "Certificateurs", back_populates="fiches_certificateurs"
    )

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesCodesNSF(Base):
    __tablename__ = "fiches_codes_NSF"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    code_nsf_id = Column(Integer, ForeignKey("codes_NSF.id"))
    fiche = relationship("Fiches", back_populates="fiches_codes_nsf")
    code_NSF = relationship("CodesNSF", back_populates="fiches_codes_NSF")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesCodesROME(Base):
    __tablename__ = "fiches_codes_rome"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    code_rome_id = Column(Integer, ForeignKey("codes_rome.id"))
    fiche = relationship("Fiches", back_populates="fiches_codes_rome")
    codes_rome = relationship("CodesROME", back_populates="fiches_codes_rome")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesFormacodes(Base):
    __tablename__ = "fiches_formacodes"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    formacode_id = Column(Integer, ForeignKey("formacodes.id"))
    fiche = relationship("Fiches", back_populates="fiches_formacodes")
    formacodes = relationship("Formacodes", back_populates="fiches_formacodes")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesIDCC(Base):
    __tablename__ = "fiches_idcc"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    idcc_id = Column(Integer, ForeignKey("idcc.id"))
    fiche = relationship("Fiches", back_populates="fiches_idcc")
    idcc = relationship("IDCC", back_populates="fiches_idcc")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FichesCCN(Base):
    __tablename__ = "fiches_ccn"
    id = Column(Integer, primary_key=True)
    fiche_id = Column(Integer, ForeignKey("fiches.id"))
    ccn_id = Column(Integer, ForeignKey("ccn.id"))
    fiche = relationship("Fiches", back_populates="fiches_ccn")
    ccn_related = relationship("CCN", back_populates="fiches_ccn")

    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


from config import get_settings

settings = get_settings()
engine = create_engine(
    settings.db_url, echo=True
)  # <-  PASS IN DATABASE CREDENTIALS HERE


# create all tables
# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)


def create_tables():
    Base.metadata.create_all(engine)


def drop_tables():
    Base.metadata.drop_all(engine)
