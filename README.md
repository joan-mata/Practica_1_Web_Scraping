# Pràctica 1 – Web Scraping: EV Database

Aquest projecte forma part de la **Pràctica 1 de l’assignatura M2.951 – Tipologia i cicle de vida de les dades (UOC)**.  
L’objectiu és implementar un procés complet de **web scraping amb Python** per obtenir i estructurar dades tècniques i comercials de vehicles elèctrics a partir del lloc web **[EV Database](https://ev-database.org)**.

El scraper s’ha desenvolupat amb **Selenium** i **BeautifulSoup**, i extreu informació sobre cada model: marca, preu, autonomia, capacitat de bateria, potència, consum i dimensions.  
Les dades es guarden en un fitxer CSV (`dataset/ev_dataset.csv`) per facilitar la seva anàlisi posterior.


## Requisits i dependències

Requereix **Python 3.10 o superior** i les següents llibreries:

- `requests`  
- `beautifulsoup4`  
- `selenium`  
- `webdriver-manager`  
- `pandas`

### Instal·lació de dependències

```bash
pip install -r requirements.txt
```

## Execució
	1.	Assegura’t de tenir instal·lat Google Chrome.
	2.	Executa el projecte amb:

```bash
python main.py
```

El scraper recorrerà les pàgines de EV Database i crearà el fitxer: (`dataset/ev_dataset.csv`)

El codi inclou esperes aleatòries i un límit de vehicles per evitar bloquejos del servidor.



## Resultat

El dataset final conté, entre altres, les variables següents:

Brand, Model, Price, Availability, Battery, Range, Power, Speed, Consumption, Dimensions, Seats

El fitxer s’ha publicat a Zenodo sota llicència CC BY-SA 4.0.
DOI: https://doi.org/10.5281/zenodo.17575547


## Aspectes legals

Aquest projecte s’ha dut a terme amb finalitats acadèmiques i respectant les bones pràctiques de web scraping:
ús moderat de peticions, esperes entre consultes i aturada automàtica en detectar bloquejos.
S’ha revisat el fitxer robots.txt del lloc web i s’han limitat les peticions per evitar sobrecàrregues al servidor.


## Autoria
	•	Ari Pidevall
	•	Joan Mata Pàrraga

Universitat Oberta de Catalunya (UOC)
Màster en Ciència de Dades · Curs 2025-1



## Llicència

El codi font s’ha publicat sota MIT License.

El dataset (ev_dataset.csv) es distribueix sota Creative Commons BY-SA 4.0.
