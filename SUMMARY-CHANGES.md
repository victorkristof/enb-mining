# Summary of changes as per Paula's email on 25.01.22

- issue_id = 1 is a curtain raiser issue
  Was implemented already, the type was "first", renamed to "curtain-raiser".

- Generally: As discussed last time, we cannot correct for all misspellings found in the ENBs
  Added processing to add spacing for "andParty" and "andPARTY" cases.

- id = 1597 to 1601
  Added spacing for "G77and China".
  Added Valdivia Group.
  Added aliases for GRULAC and African Group.

- id = 7541 and 7542
  Added rule for OBH when there is a dot instead of a comma to close the interaction

- id = 8377 and 8379
  Added alias for Umbrella Group: Umbrella Group (a fluid grouping of non-EU Annex I countries)

- id = 9309
  Added alias for Visegrad Group: VISEGRAD Group of central European countries

- id = 11518 to 11521
  Added alias for EIG: Environmental Integrity Group (Switzerland, Republic of Korea and Mexico)

- id = 12620 and 12621
  Added alias for Central Group: CENTRAL GROUP 11

- id = 12905 to 12908
  Added alias for EIG: Environmental Integrity Group (a coalition of countries including Switzerland, Mexico and the Republic of Korea)

- id = 12909 and 12910
  Added alias for LDCs: Least Developed Countries (LDCs) group

- id = 16341 to 16343
  Added alias for CACAM: CACAM group

- id = 19125 to 1912
  Added alias for LDCs: LDC GROUP

- id = 38951
  Could not fix the missing comma after Umbrella Group: the OBH interactions require the structure `<PAR><,><OBH><,>`.

- General
  Normalize "US$" to "$" to prevent parsing interactions for US

- id = 3419 to 3426
  Separate the `clean` function into `normalize` (improve the format of the sentence) and `preprocess` (prepare it for tagging, should not be saved)

- id = 15062 to 15065
  Added alias for Central Group: Central Group of Eleven (CG-11)

- id = 15154
  Added alias for G77: G-77/ CHINA

- id = 41 and 42
  Added "onbehalf" as marker

- id = 161 and 165
  Added rule to match "Party (on behalf of Party/Grouping)"

- id = 290 and 291
  Add space before opening parenthesis to handle cases such as "Franc(on behalf of ...)"

- id = 328 and 329
  "The Philippines, on behalf ofG-77 and China" too specific

- id = 3663 to 3665
  Added space after dot, such as in "...developing country scientists involvement in the IPCC.MALAYSIA, CHINA, the PHILIPPINES and INDIA favored..." -> this happens quite often, not just in this one sentence as suggested in Paula's email

- id = 6163 to 6172
  Added "Korea" as alias for "South Korea"

- id = 18070 to 18074
  Make interventions hashable, so that we can use them in sets to obtain unique interventions from sentences.

- adding a further variable (column) indicating the negotiation group (COP, SBSTA, SBI, contact group) and agenda item (CDM, etc.) during which the sentence is recorded, based on the subheadings available in the ENBs?
  That's a bit too much for now I think. I'll look into it when I have solved all other issues.

- id = 76
  Add a special `<Others>` party in parties.txt that will match "and [many] others" in the text, which happens quite often. It's then the responsibility of the researcher to discard them or not.

- id = 110
  Solved above

- id = 216 to 235
  Solved above

- id = 352
  "France, on behalf of the EU, and supported by..." impossible to handle the "double" interaction for France

- id = 437
  Solved above

- id = 1114
  Allow missing commas in aggreements

- id = 1586
  Added accent in Côte d'Ivoire

- id = 38492
  Solved above

- id = 3919 and 3920
  Solved above

- id = 10102 (issue_id = 84)
  Solved above

- id = 44013
  On behalf/joint statement: still not clear to me which one we would like...

- id = 3991
  Difficult to separate "INDIAnoted" into two words easily

- id = 15537, issue_id = 131
  Will not implement because opposition marker too far from "the EU"

- id = 15539, issue_id = 131
  Will not implement because the "reversed" structure is too complex: "With the Russian Federation, and opposed by Samoa, Palau, Micronesia and Brazil..."

- id = 15728, issue_id = 132
  Match "with" as agreement: "AUSTRALIA, with the RUSSIAN FEDERATION and opposed by SAMOA, PALAU, the FEDERATED STATES OF MICRONESIA and BRAZIL..."

- id = 21991 (issue_id = 209)
  Add "and opposed" as opposition marker: "BRAZIL, on behalf of the G-77/China, and opposed by CANADA, the EU, RUSSIAN FEDERATION and AUSTRALIA, proposed..."

- id = 37490 (issue_id = 446
  Solved above

- id = 38853
  Solved above

- id = 40065 (issue_id = 463)
  Structure too complex: "The EU reiterated that ... and, with the US, AUSTRALIA, CANADA and JAPAN, sought..."

- id = 40110 (issue_id = 464)
  Same: "The US explained that ... and, supported by AUSTRALIA, the EU, NEW ZEALAND, MEXICO and AOSIS, opposed..."

- id = 457
  Nothing to be done

- id = 455
  The entities are too fart apart (but/while)

- id = 21142
  The entities are too fart apart (but/while)

- id = 27693
  Solved above

- id = 459-460
  Solved by tagging specific words ("and", "with", ...) with custom tags

- id = 461-490
  The entities are too fart apart (but/while)

- id = 24770
  A sentence that starts with "While"

- id = 1696 and following
  Too specific

- id = 29511
  Because of previous rule with "and opposed" it now records false oppositions between Canada and Saudi Arabia/Argentina (instead of none): "China, supported by Saudi Arabia and Argentina and opposed by Canada, introduced text stating..."

- id = 17800 (issue_id == 157)
  Added "also on behalf" as marker

- id = 140 to 181
  Impossible to get support because of typo and possessive form ("China's")

- id = 742 to 753
  Implement list of sentences to ignore?

- id = 754 to 864
  Same

- id = 1426 to 1437
  Same

- sentence in issue_id == 73
  Changed rule for agreement: final "and"/"with" is optional now
