import csv
import time
import random
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    NoSuchElementException,
    ElementClickInterceptedException,
)

# CONFIGURATION

TOTAL_PROFILS_CIBLE = 80
MAX_PAGES = 15

MOT_CLE = "data open to work"

FICHIER_OUTPUT = Path(__file__).resolve().parent / "candidats_linkedin.csv"

FICHIER_DEBUG = Path(__file__).resolve().parent / "linkedin_debug_final.html"


# MOTS-CLES DOMAINES

MOTS_DATA = [
    "data",
    "data analyst",
    "data scientist",
    "data science",
    "data engineer",
    "data engineering",
    "data analyste",
    "data scientist",
    "data engineer",
    "big data",
    "business intelligence",
    "business analyst",
    "bi ",
    "power bi",
    "tableau",
    "sql",
    "machine learning",
    "machine-learning",
    "analytics",
    "data mining",
    "data warehouse",
    "etl",
]

MOTS_AI = [
    "artificial intelligence",
    "artificial-intelligence",
    "ai ",
    "ai engineer",
    "ai developer",
    "machine learning",
    "deep learning",
    "computer vision",
    "nlp",
    "natural language processing",
    "generative ai",
    "genai",
    "llm",
    "neural network",
    "robotics",
]

MOTS_IT = [
    "software engineer",
    "software developer",
    "web developer",
    "developer",
    "programmer",
    "computer science",
    "it ",
    "information technology",
    "devops",
    "cloud",
    "cybersecurity",
    "cyber security",
    "system administrator",
    "systems administrator",
    "network engineer",
    "network administrator",
    "full stack",
    "frontend",
    "front end",
    "backend",
    "back end",
    "java",
    "python",
    "javascript",
    "php",
    "c++",
]


# CONNEXION

options = webdriver.ChromeOptions()

# Si tu veux utiliser un Chrome déjà ouvert :
# options.add_experimental_option(
#     "debuggerAddress",
#     "127.0.0.1:9222"
# )

driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 20)


# FONCTIONS UTILITAIRES


def normaliser(texte):
    """Nettoie un texte pour faciliter les comparaisons."""

    if not texte:
        return ""

    return " ".join(texte.lower().replace("\n", " ").split())


def determiner_domaine(texte):
    """
    Détermine si le profil correspond à DATA, AI ou IT.
    """

    texte_normalise = normaliser(texte)

    domaines = []

    # DATA
    for mot in MOTS_DATA:

        if mot.lower() in texte_normalise:
            domaines.append("DATA")
            break

    # AI
    for mot in MOTS_AI:

        if mot.lower() in texte_normalise:
            domaines.append("AI")
            break

    # IT
    for mot in MOTS_IT:

        if mot.lower() in texte_normalise:
            domaines.append("IT")
            break

    # Suppression des doublons
    domaines = list(dict.fromkeys(domaines))

    if not domaines:
        return None

    return " / ".join(domaines)


def detecter_open_to_work(texte):
    """
    Détecte uniquement si Open To Work est réellement visible
    dans le texte du résultat.

    On ne considère PAS l'absence du texte comme 'No'.
    """

    texte_normalise = normaliser(texte)

    mots_open = [
        "open to work",
        "open-to-work",
        "à la recherche d'opportunités",
        "à la recherche de nouvelles opportunités",
        "disponible pour de nouvelles opportunités",
        "en recherche d'emploi",
    ]

    for mot in mots_open:

        if mot in texte_normalise:
            return "Détecté"

    return "Non détecté"


def extraire_url_profil(voir):
    """
    Le lien 'Voir' pointe actuellement vers la page de recherche.

    Nous cherchons donc le <a> parent du profil.
    D'après notre test, il se trouve au niveau supérieur
    du lien 'Voir'.
    """

    try:

        # Dans notre structure observée :
        #
        # <a> PROFIL
        #   ...
        #   <a> Voir </a>
        #
        # On cherche donc le deuxième <a> dans les ancêtres.

        ancres = voir.find_elements(By.XPATH, "ancestor::a")

        # Selenium retourne les ancêtres du plus proche au plus éloigné.
        # Le premier peut être le lien Voir lui-même.
        # On cherche un href différent du lien de recherche.

        for a in ancres:

            try:

                href = a.get_attribute("href")

                if not href:
                    continue

                if "/in/" in href:
                    return href

            except Exception:
                continue

        # Deuxième tentative : parent <a>
        try:

            parent_a = voir.find_element(By.XPATH, "ancestor::a[2]")

            href = parent_a.get_attribute("href")

            if href and "/in/" in href:
                return href

        except Exception:
            pass

    except Exception:
        pass

    return ""


def extraire_profil_depuis_voir(voir):
    """
    Extrait un profil à partir du lien 'Voir'.

    Structure observée dans notre page :

        Utilisateur LinkedIn
        Data scientist student
        Gouvernorat Tunis, Tunisie
        Voir
        Compétences : Data Streaming
    """

    try:

        # Trouver le bloc parent contenant les informations

        parent = voir

        # Notre test a montré que le bloc utile est à environ
        # 4 niveaux au-dessus de 'Voir'.

        for _ in range(4):

            parent = parent.find_element(By.XPATH, "..")

        texte_bloc = parent.text.strip()

        if not texte_bloc:
            return None

        # Récupérer les paragraphes <p>

        paragraphes = parent.find_elements(By.XPATH, ".//p")

        textes_p = []

        for p in paragraphes:

            try:

                texte = p.text.strip()

                if texte:
                    textes_p.append(texte)

            except Exception:
                pass

        # NOM

        nom = ""

        if len(textes_p) >= 1:

            nom = textes_p[0].strip()

        # POSTE

        poste = ""

        if len(textes_p) >= 2:

            poste = textes_p[1].strip()

        # LOCALISATION

        localisation = ""

        if len(textes_p) >= 3:

            localisation = textes_p[2].strip()

        # URL DU PROFIL

        url_profil = extraire_url_profil(voir)

        # DOMAINE
        domaine = determiner_domaine(texte_bloc)

        # OPEN TO WORK
        open_to_work = detecter_open_to_work(texte_bloc)

        # SNIPPET

        snippet = ""

        if len(textes_p) >= 4:

            snippet = " | ".join(textes_p[3:])

        # RESULTAT

        return {
            "Nom": nom,
            "Poste": poste,
            "Localisation": localisation,
            "Domaine": domaine,
            "Open To Work": open_to_work,
            "URL LinkedIn": url_profil,
            "Informations": snippet,
        }

    except StaleElementReferenceException:

        return None

    except Exception as e:

        print("⚠️ Erreur extraction profil :", e)

        return None


def recuperer_profils_page():
    """
    Récupère tous les profils actuellement affichés.

    IMPORTANT :
    On utilise les liens 'Voir', car ce sont les éléments
    que notre analyse réelle a trouvés.
    """

    profils = []

    try:

        liens_voir = driver.find_elements(By.XPATH, "//a[normalize-space()='Voir']")

    except Exception:

        liens_voir = []

    print()
    print(f"👁️ Liens 'Voir' détectés : {len(liens_voir)}")

    # Extraction

    for index in range(len(liens_voir)):

        try:

            # On récupère à nouveau les éléments à chaque tour.
            # Cela évite les problèmes StaleElement.
            liens_actuels = driver.find_elements(
                By.XPATH, "//a[normalize-space()='Voir']"
            )

            if index >= len(liens_actuels):
                break

            voir = liens_actuels[index]

            profil = extraire_profil_depuis_voir(voir)

            if not profil:
                continue

            # Vérification domaine

            if not profil["Domaine"]:

                print(f"   ⏭️ Ignoré : " f"{profil['Poste']}")

                continue

            profils.append(profil)

            print()
            print(f"   ✅ Profil {len(profils)}")

            print(f"      Nom          : " f"{profil['Nom']}")

            print(f"      Poste        : " f"{profil['Poste']}")

            print(f"      Localisation : " f"{profil['Localisation']}")

            print(f"      Domaine      : " f"{profil['Domaine']}")

            print(f"      Open To Work : " f"{profil['Open To Work']}")

            print(
                f"      URL          : " f"{profil['URL LinkedIn'] or 'Non disponible'}"
            )

        except StaleElementReferenceException:

            print("⚠️ Élément devenu obsolète.")

        except Exception as e:

            print(f"⚠️ Erreur profil {index + 1} : {e}")

    return profils


def page_contient_resultats():
    """
    Vérifie les résultats en utilisant la structure réelle
    observée dans nos tests.

    NE PAS utiliser /in/ ici.
    """

    try:

        liens = driver.find_elements(By.XPATH, "//a[normalize-space()='Voir']")

        return len(liens) > 0

    except Exception:

        return False


def sauvegarder_profil(profil, urls_existantes, cles_existantes, writer, fichier):
    """
    Sauvegarde immédiatement un profil.
    """

    url = profil["URL LinkedIn"]

    # Déduplication par URL si disponible

    if url:

        if url in urls_existantes:

            return False

    # Déduplication de secours
    #
    # Comme certains profils peuvent ne pas exposer leur URL,
    # on utilise Poste + Localisation + Informations.

    cle = (
        normaliser(profil["Nom"]),
        normaliser(profil["Poste"]),
        normaliser(profil["Localisation"]),
        normaliser(profil["Informations"]),
    )

    if cle in cles_existantes:

        return False

    # Écriture
    writer.writerow(profil)

    fichier.flush()

    if url:

        urls_existantes.add(url)

    cles_existantes.add(cle)

    return True


def cliquer_page_suivante():
    """
    Clique sur 'Suivant' et attend le changement de page.
    """

    try:

        # Récupérer la première fiche actuelle

        ancien_texte = ""

        try:

            liens = driver.find_elements(By.XPATH, "//a[normalize-space()='Voir']")

            if liens:

                ancien_texte = liens[0].find_element(By.XPATH, "../..").text

        except Exception:
            pass

        # Chercher le bouton/lien Suivant

        xpath_suivant = (
            "//button[normalize-space()='Suivant']"
            " | "
            "//a[normalize-space()='Suivant']"
            " | "
            "//button[contains(@aria-label,'Suivant')]"
            " | "
            "//button[contains(@aria-label,'Next')]"
            " | "
            "//a[contains(@aria-label,'Suivant')]"
            " | "
            "//a[contains(@aria-label,'Next')]"
        )

        boutons = driver.find_elements(By.XPATH, xpath_suivant)

        bouton = None

        for b in boutons:

            try:

                if b.is_displayed() and b.is_enabled():

                    bouton = b
                    break

            except Exception:
                continue

        if bouton is None:

            print("🏁 Bouton 'Suivant' introuvable.")

            return False

        # Scroll vers le bouton

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bouton)

        time.sleep(1)

        # Cliquer

        try:

            bouton.click()

        except ElementClickInterceptedException:

            driver.execute_script("arguments[0].click();", bouton)

        except Exception:

            driver.execute_script("arguments[0].click();", bouton)

        print("➡️ Page suivante cliquée.")

        # Attendre le changement

        for _ in range(20):

            time.sleep(1)

            nouveaux_liens = driver.find_elements(
                By.XPATH, "//a[normalize-space()='Voir']"
            )

            if not nouveaux_liens:
                continue

            try:

                nouveau_texte = nouveaux_liens[0].find_element(By.XPATH, "../..").text

            except Exception:

                nouveau_texte = ""

            if nouveau_texte != ancien_texte:

                print("✅ Nouvelle page chargée.")

                return True

        print("⚠️ La page suivante n'a pas " "été détectée comme nouvelle.")

        return True

    except Exception as e:

        print("❌ Erreur pagination :", e)

        return False


# PROGRAMME PRINCIPAL

try:

    # CONNEXION LINKEDIN

    print()
    print("=" * 70)
    print("🔐 CONNEXION LINKEDIN")
    print("=" * 70)

    driver.get("https://www.linkedin.com/login")

    # IMPORTANT :
    # Mets tes identifiants ici.

    EMAIL_LINKEDIN = "YOUR_EMAIL_HERE"
    MOT_DE_PASSE_LINKEDIN = "YOUR_PASSWORD_HERE"

    email = wait.until(
        EC.element_to_be_clickable((By.XPATH, "(//input[@type='email'])[2]"))
    )

    email.send_keys(EMAIL_LINKEDIN)

    time.sleep(random.uniform(1, 2))

    password = wait.until(
        EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[2]"))
    )

    password.send_keys(MOT_DE_PASSE_LINKEDIN)

    time.sleep(random.uniform(8, 10))

    time.sleep(5)

    print()
    print("✅ CONNEXION TERMINEE")

    # OUVERTURE PEOPLE

    print()
    print("=" * 70)
    print("🔎 OUVERTURE DE LA RECHERCHE PEOPLE")
    print("=" * 70)

    url_recherche = (
        "https://www.linkedin.com/search/results/people/"
        "?keywords=data%20open%20to%20work"
    )

    driver.get(url_recherche)

    time.sleep(5)

    # FILTRE TUNISIE

    print()
    print("=" * 70)
    print("📍 FILTRE TUNISIE")
    print("=" * 70)

    print()
    print("Fais maintenant MANUELLEMENT dans LinkedIn :")

    print()
    print("1️⃣ Clique sur « Lieux » / « Locations »")

    print("2️⃣ Sélectionne « Tunisie »")

    print("3️⃣ Applique le filtre")

    print()
    print("⚠️ Ne change PAS la recherche « data ».")

    print()
    print("Quand les résultats tunisiens sont affichés :")

    print("➡️ Reviens ici et appuie sur ENTRÉE.")

    input("\n👉 Appuie sur ENTRÉE pour commencer...")

    # ATTENTE DES PREMIERS RESULTATS

    print()
    print("=" * 70)
    print("🔎 RECHERCHE DES PROFILS")
    print("=" * 70)

    print()
    print("⏳ Attente des résultats...")

    for _ in range(20):

        if page_contient_resultats():

            break

        time.sleep(1)

    if not page_contient_resultats():

        print()
        print("❌ Aucun lien 'Voir' détecté.")

        print("⚠️ Vérifie que les résultats " "tunisiens sont bien affichés.")

        # Sauvegarde diagnostic
        with open(FICHIER_DEBUG, "w", encoding="utf-8") as f:

            f.write(driver.page_source)

        print()
        print("💾 HTML sauvegardé :")

        print(FICHIER_DEBUG)

        input("\n👉 Appuie sur ENTRÉE pour fermer...")

        raise SystemExit

    print("✅ Résultats détectés.")

    # PREPARATION CSV

    print()
    print("=" * 70)
    print("💾 PREPARATION DU CSV")
    print("=" * 70)

    print()
    print("📁 Fichier :")

    print(FICHIER_OUTPUT)

    # Récupérer les URLs déjà présentes

    urls_existantes = set()
    cles_existantes = set()

    mode = "a"

    fichier_existe = FICHIER_OUTPUT.exists() and FICHIER_OUTPUT.stat().st_size > 0

    fichier_csv = open(FICHIER_OUTPUT, mode, newline="", encoding="utf-8-sig")

    colonnes = [
        "Nom",
        "Poste",
        "Localisation",
        "Domaine",
        "Open To Work",
        "URL LinkedIn",
        "Informations",
    ]

    writer = csv.DictWriter(fichier_csv, fieldnames=colonnes)

    if not fichier_existe:

        writer.writeheader()

        fichier_csv.flush()

    # Lire les anciens profils

    if fichier_existe:

        try:

            with open(
                FICHIER_OUTPUT, "r", newline="", encoding="utf-8-sig"
            ) as ancien_csv:

                lecteur = csv.DictReader(ancien_csv)

                for ligne in lecteur:

                    url = (ligne.get("URL LinkedIn", "") or "").strip()

                    if url:

                        urls_existantes.add(url)

                    cle = (
                        normaliser(ligne.get("Nom", "")),
                        normaliser(ligne.get("Poste", "")),
                        normaliser(ligne.get("Localisation", "")),
                        normaliser(ligne.get("Informations", "")),
                    )

                    cles_existantes.add(cle)

        except Exception as e:

            print("⚠️ Impossible de lire " "les anciens profils :", e)

    # COLLECTE

    total_enregistre = len(cles_existantes)

    pages_sans_nouveau = 0

    page = 1

    while page <= MAX_PAGES and total_enregistre < TOTAL_PROFILS_CIBLE:

        print()
        print("=" * 70)
        print(f"📄 PAGE {page}/{MAX_PAGES}")

        print(f"🎯 Profils enregistrés : " f"{total_enregistre}/{TOTAL_PROFILS_CIBLE}")

        print("=" * 70)

        # Scroll progressif

        for _ in range(4):

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(random.uniform(1, 2))

        # Extraction

        profils = recuperer_profils_page()

        print()
        print(
            f"📊 Profils correspondant " f"aux domaines DATA/AI/IT : " f"{len(profils)}"
        )

        nouveaux = 0

        for profil in profils:

            if total_enregistre >= TOTAL_PROFILS_CIBLE:

                print()
                print("=" * 70)
                print("🎯 OBJECTIF ATTEINT !")
                print(f"👥 {total_enregistre} profils enregistrés.")
                print(f"💾 Données sauvegardées dans : {FICHIER_OUTPUT}")
                print("=" * 70)

                fichier_csv.flush()
                fichier_csv.close()

                print()
                print("🌐 Fermeture automatique de Chrome...")

                driver.quit()

                print("✅ Chrome fermé.")
                print("✅ Programme terminé.")

                raise SystemExit

            ajoute = sauvegarder_profil(
                profil, urls_existantes, cles_existantes, writer, fichier_csv
            )

            if ajoute:

                total_enregistre += 1

                nouveaux += 1

                print()
                print(
                    f"💾 ENREGISTRÉ " f"({total_enregistre}/" f"{TOTAL_PROFILS_CIBLE})"
                )

        # Vérification page

        if nouveaux == 0:

            pages_sans_nouveau += 1

            print()
            print(
                f"⚠️ Aucun nouveau profil "
                f"enregistré sur cette page "
                f"({pages_sans_nouveau}/3)."
            )

        else:

            pages_sans_nouveau = 0

        # Stop si 3 pages sans nouveaux profils

        if pages_sans_nouveau >= 3:

            print()
            print("🛑 3 pages consécutives " "sans nouveau profil.")

            break

        # Objectif atteint

        if total_enregistre >= TOTAL_PROFILS_CIBLE:

            print()
            print("🎯 OBJECTIF DE 80 PROFILS ATTEINT !")

            break

        # Page suivante

        if page >= MAX_PAGES:

            break

        print()

        if not cliquer_page_suivante():

            print("🏁 Impossible de continuer " "vers une nouvelle page.")

            break

        page += 1

        time.sleep(random.uniform(2, 4))

    # FIN

    fichier_csv.flush()
    fichier_csv.close()

    print()
    print("=" * 70)
    print("🏁 COLLECTE TERMINÉE")
    print("=" * 70)

    print()
    print(f"👥 Profils enregistrés : {total_enregistre}")
    print(f"📄 Pages parcourues : {page}")

    print()
    print("💾 CSV :")
    print(FICHIER_OUTPUT)

    # FERMETURE AUTOMATIQUE

    print()
    print("🌐 Fermeture automatique de Chrome...")

    driver.quit()

    print("✅ Chrome fermé.")
    print("✅ Programme terminé.")

finally:

    try:
        if driver:
            driver.quit()
    except Exception:
        pass
