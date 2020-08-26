# Analyse Schooltoewijzing Antwerpen 2020

## Overzicht Data

De geanonimiseerde dataset bevat **18791** records. Iedere record staat voor de applicatie van een kind voor een school. Respectievelijk aangegeven door KindId en SchoolId. Na filteren van applicaties in periode 3 blijven nog **16597** records over. 

### Periodes

Applicaties gebeuren in periodes, periode 1 is de voorrangsperiode waarin getracht wordt om ieder kind met recht op voorrang toe te wijzen aan de school naar voorkeur. Periode 2 is de reguliere periode, leerlingen uit deze periode geven een voorkeur op voor verschillende scholen, en krijgen zelf een toevalsnummer toegewezen dat de voorkeur van de scholen voor de leerling voorstelt. Voorkeuren van leerlingen en voorkeuren van scholen worden in beschouwing genomen via het Boston algoritme. Periode 3 wordt in deze analyse buiten beschouwing gelaten.

### Indicator leerlingen

Scholen verdelen hun capaciteit over indicator leerlingen en niet-indicator leerlingen. Leerlingen met de indicator status worden getracht eerst toe te wijzen aan de indicator capaciteit van een school, idem gebeurt met leerlingen met een niet-indicator status. Indien er op een school niet voldoende vrije indicator capaciteit is, dan kan een indicator leerling alsnog toegewezen worden aan de niet-indicator capaciteit van een school. Dit gebeurt alsook met niet-indicator leerlingen.

Aantal applicaties per periode
<center>

| Periode | IND   | nIND | Onbepaald | Totaal |
| :-----: | ----- | ---- | --------- | ------ |
|    1    | 1123  | 627  | 4         | 1754   |
|    2    | 9868  | 4975 | 0         | 14843  |
| totaal  | 10991 | 5602 | 4         | 16597  |

</center>


Aantal **verschillende** kinderen per periode:

<center>

| Periode | IND  | nIND | Onbepaald | Totaal |
| :-----: | ---- | ---- | --------- | ------ |
|    1    | 1111 | 615  | 4         | 1730   |
|    2    | 3642 | 1659 | 0         | 5301   |
| totaal  | 4629 | 2274 | 4         | 7031   |

</center>

### Applicaties over meerdere periodes

Er zijn **1730** leerlingen met een voorrangstatus (applicatie in periode 1). Deze leerlingen hebben ook het recht om te appliceren in de reguliere periode (periode 2). Wanneer dit het geval is, dan zullen zij zowel een school toegewezen krijgen volgens hun voorrangsrecht in periode 1, als een **?andere?** school op basis van de Boston toewijzing in periode 2. Er kan maximaal 1 school toegewezen worden per leerling per periode.

In de huidige dataset werden **geen** leerlingen gevonden die zowel een applicatie hadden in periode 1 als in periode 2.

### Status onbepaald

**4** leerlingen met indicator status onbepaald werden teruggevonden in periode 1. Leerlingen met deze status worden toegewezen aan **indicatorplaatsen** in hun respectievelijke school van voorkeur (indien nog voldoende indicatorcapaciteit).

## Pre-Processing van data

Om de simulatie uit te voeren was het noodzakelijk om enkele hulpvariabelen te berekenen uit de originele dataset.

### Unieke SchoolID

Applicaties van leerlingen gebeuren enerzijds naar scholen, maar ook naar een groep binnen een school (A-stroom/B-stroom). Sommige scholen bieden zowel de A-stroom als de B-stroom aan, waardoor het niet volstaat om een applicatie van een leerling te linken aan het originele **schoolId**. In de simulatie wordt er daarom gebruik gemaakt van een samengestelde nieuwe id voor de scholen: **[school_id]_[groep]**. Op basis van deze nieuwe ID kunnen 100 scholen onderscheiden worden waarvoor leerlingen kunnen appliceren.


### IND - nIND Capaciteit

Scholen hebben een maximale capaciteit en een percentage indicator capaciteit. In de simulatie worden deze twee variabelen gebruikt om de capaciteit te berekenen voor indicator leerlingen en de capaciteit voor niet-indicator leerlingen.
Omdat capaciteit steeds een geheel getal moet zijn, moet er doordacht omgegaan worden met afronden van capaciteit. De conventie in de simulatie gaat als volgt: rond af naar het dichtsbijzijnde gehele getal, bij 0.5 wordt er steeds naar het kleinste geheel getal afgerond.
Deze conventie zorgt ervoor dat in sommige gevallen één plaats verloren gaat, wanneer beide capaciteiten naar onder worden afgerond. In deze gevallen wordt nadien één plaats extra bij de **niet-indicator** capaciteit opgeteld. Zo blijft het na te streven indicator percentage steeds gerespecteerd.

## Toewijzingsmechanisme

Alle applicaties in de huidige dataset worden verwerkt in twee fasen. Fase 1 (Pre-assign) verwerkt de leerlingen uit de voorrangsperiode. Fase 2 (Boston) verwerkt de applicaties uit periode 2 via het boston algoritme.

### Pre-Assign

In fase 1 worden alle applicaties uit periode 1 beschouwd. Dit zijn in totaal **1754** applicaties van **1730 verschillende** kinderen. **24** kinderen deden elks 2 applicaties in periode 1.

De simulatie zal voor ieder kind uit periode 1 kijken of de school van voorkeur van het kind een plaats heeft. Indicator plaatsen en niet-indicatorplaatsen worden in overweging genomen, maar een kind zal steeds toegang tot de school krijgen indien er vrije capaciteit is (ongeacht de indicatorstatus).

In de huidige simulatie konden **alle** kinderen uit periode 1 een plaats krijgen in hun school van voorkeur. Er werd daarom in de simulatie geen extra rekening gehouden met de voorrangscodes die toegekend werden aan ieder kind.

### Boston

Na fase 1 worden de overige kinderen in de reguliere periode verdeeld over de scholen via het Boston algoritme. Boston is een verdelingsmechanisme ontwikkeld voor [...].

Boston werkt als volgt:
- Stap 1: Vind voor iedere school de leerlingen die deze school als eerste keuze hebben. Plaats leerlingen op deze school in volgorde van voorkeur van de school voor de leerlingen, tot school geen capaciteit meer heeft, of geen leerlingen meer zijn met deze school als voorkeur.
- Stap i: Herhaal werkwijze voor elke keuze *i* tot alle leerlingen verdeeld zijn, alle scholen volzet zijn of leerlingen geen overige keuzes hebben.

In deze simulatie houden we rekening met **14843** applicaties. De iteraties van het algoritme komen overeen met de rangordes van de keuzes die studenten geven aan de scholen. Het maximaal aantal iteraties is daarom gelijk aan het totaal aantal verschillende scholen (100).
In iedere iteratie wordt voor iedere school gezocht naar alle leerlingen die voorkeur geven aan deze school. Deze *applicaties* voor een school zijn dus voorzien van een **voorkeursnummer** van de leerling (welke moet overeenkomen met het iteratienummer, maar in praktijk soms anders is), alsook een **toevalsnummer**. Dit toevalsnummer is willekeurig gekozen en wordt gebruikt om de voorkeur van de school naar de leerling uit te drukken.
De leerlingen worden per school gerangschikt op basis van hun toevalsnummer (van laag naar hoog), en worden volgens deze rangschikking toegelaten tot de school.
Er wordt nu in rangorde gekeken of er plaats is voor de leerling. Hierbij wordt voor een indicator leerling eerst getest of er een indicatorplaats is op de school, zoniet wordt de leerling toegewezen aan een niet-indicatorplaats. Idem voor niet-indicator leerlingen.

## Resultaten

Toekenningen:
<center>

| Fase       | Toekenningen |
| :--------- | ------------ |
| Pre-assign | 1730         |
| Boston     | 4281         |
| Totaal     | 6011         |

</center>

In totaal werden in de simulatie **6011** kinderen voorzien van een toelating tot een school. **1730** van deze toelatingen werden toegekend tijdens fase 1 op basis van het voorkeursrecht. **4281** toelatingen werden via het Boston algoritme toegekend. Op een totaal van **6791** kinderen betekent dit dat er **780** kinderen overbleven zonder toegekende school aan het einde van de simulatie. Opm: +- 80% van deze leerlingen gaf 3 keuzes of minder op.

Niet toegekend:

<center>

| Aantal voorkeuren | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | Totaal |
| ----------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ------ |
| Kinderen          | 241 | 153 | 204 | 83  | 68  | 18  | 9   | 3   | 1   | 780    |

</center>

### Invloed op keuze

De cijfers uit onderstaande tabellen geven duiding over de toekenningen per voorkeur. Beide tabellen verschillen subtiel, in de zin dat de keuzerang van een school voor een leerling een door de simulatie **berekende** eenheid is. Voorkeuren voor scholen worden gerangschikt volgens de opgegeven **voorkeur**, vervolgens wordt gebruik gemaakt van de rangordes van de scholen. Anders is de tabel met opgegeven voorkeur, die in principe dezelfde cijfers moet uitkomen, maar omdat de opgeven voorkeuren in de data niet altijd overeenkomen met het aantal opgeven scholen, bestaan er kleine afwijkingen. Uit beide tabellen valt wel de overduidelijke meerderheid op van leerlingen die hun eerste keuze toegewezen kregen (+-93%).

<center>

| keuzerang school | aantal toekenningen |
| ---------------- | ------------------- |
| 1                | 5602                |
| 2                | 260                 |
| 3                | 103                 |
| 4                | 27                  |
| 5                | 16                  |
| 6                | 2                   |
| 8                | 1                   |
| totaal           | 6011                |

| Opgegeven voorkeur | aantal toekenningen |
| ------------------ | ------------------- |
| 1                  | 5597                |
| 2                  | 263                 |
| 3                  | 105                 |
| 4                  | 27                  |
| 5                  | 16                  |
| 6                  | 2                   |
| 8                  | 1                   |
| totaal             | 6011                |

</center>

### Invloed verdeling IND - nIND

Het verdelingsmechanisme over indicator plaatsen en niet indicator plaatsen zal geen leerlingen weigeren indien er vrije capaciteit is op een school. Onderstaande tabel geeft weer hoeveel leerlingen per status een plaats kregen in de capaciteit van die status. Het merendeel van de leerlingen werd ingedeeld volgens hun status **(3670 + 1795)**.

<center>

|            | IND status  | nIND status | totaal |
| ---------- | ---- | ---- | ------ |
| **IND toegekend**    | 3670 | 445  | 4115   |
| **nIND toegekend**   | 101  | 1795 | 1896   |
| **totaal** | 3771 | 2240 | 6011   |

</center>