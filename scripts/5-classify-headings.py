import pandas as pd
import re
import numpy as np

# Load data
interventions = pd.read_csv("data/interventions.csv")
interactions = pd.read_csv("data/interactions.csv")

# Clean heading: remove text before and including first colon
interventions["heading_clean"] = interventions["heading"].str.replace(r"^[^:]+: ", "", regex=True)
interactions["heading_clean"] = interactions["heading"].str.replace(r"^[^:]+: ", "", regex=True)

# Define function to classify negotiation group
def classify_neg_group(df):
    df["neg_group"] = None
    patterns = [
        ("Joint SBI/SBSTA", ["SBI/SBSTA", "SBSTA/SBI", "JOINT MEETING OF THE SUBSIDIARY BODIES", "Agenda Items Considered Jointly by the SBSTA and SBI", "JOINT WORKING GROUP ON COMPLIANCE"]),
        ("ADP", ["ADP", "AD HOC WORKING GROUP ON THE DURBAN PLATFORM", "WORKSTREAM 1", "WORKSTREAM 2"]),
        ("ADP MINISTERIAL", ["MINISTERIAL DIALOGUE ON THE DURBAN PLATFORM FOR ENHANCED ACTION"]),
        ("Dialogue LCA", ["UNFCCC DIALOGUE"]),
        ("AWG-LCA", ["AWG-LCA", "AD HOC WORKING GROUP FOR LONG-TERM COOPERATIVE ACTION", "AD HOC WORKING GROUP ON LONG-TERM COOPERATIVE ACTION", "BAP"]),
        ("AWG-KP", ["AWG-KP", "WORKING GROUP ON FURTHER COMMITMENTS", "AWG"]),
        ("SBI", ["SBI", "SUBSIDIARY BODY FOR IMPLEMENTATION"]),
        ("SBSTA", ["SBSTA", "SUBSIDIARY BODY FOR SCIENTIFIC AND TECHNOLOGICAL ADVICE", "SUBSIDIARY BODY FOR SCIENTIFIC AND TECHNICAL ADVICE", "SUBSIDIARY BODIES FOR SCIENTIFIC AND TECHNOLOGICAL ADVICE", "SUBSIDIARY BODY ON SCIENTIFIC AND TECHNOLOGICAL ADVICE"]),
        ("Joint SBI/SBSTA", ["^SUBSIDIARY  BODIES", "^SUBSIDIARY BODIES", "^SB"]),
        ("AGBM", ["BERLIN MANDATE", "AGBM"]),
        ("AG-13", ["AG-13", "AD HOC GROUP ON ARTICLE 13"]),
        ("APA", ["APA ", "APA'", "AD HOC WORKING GROUP ON THE PARIS AGREEMENT", "COMITÉ DE PARIS"]),
        ("High-level Segment", ["HIGH-LEVEL SEGMENT", "HIGH-LEVEL  SEGMENT", "HIGH LEVEL SEGMENT"]),
        ("High-level Dialogue", ["HIGH-LEVEL MINISTERIAL", "HIGH-LEVEL EVENT"]),
        ("CMP", ["CMP", "COP/MOP", "CONFERENCE OF THE PARTIES SERVING AS THE MEETING OF THE PARTIES TO THE KYOTO PROTOCOL"]),
        ("CMA", ["CMA"]),
        ("COP", ["CONFERENCE OF THE PARTIES", "^COP ", "^COP-"]),
        ("Closing Plenary", ["CLOSING PLENARY"]),
        ("Opening Statements", ["OPENING STATEMENTS", "OPENING CEREMONY", "WELCOMING CEREMONY"]),
        ("Plenary", ["PLENARY"]),
        ("Contact Groups and Informals", ["CONTACT GROUP", "INFORMAL MEETINGS", "INFORMAL CONSULTATIONS", "FACILITATED GROUPS", "INFORMAL GROUPS", "NEGOTIATING GROUPS", "Thematic Discussions"]),
        ("Workshop", ["^EXPERT WORKSHOP", "^IN-SESSION WORKSHOP", "^PRE-SESSIONAL WORKSHOP", "^WORKSHOP", "^Mandated Event", "^Selected Mandated Events"]),
        ("Technical Expert Meetings / Dialogues", ["TECHNICAL EXPERT MEETINGS", "Technical Expert Dialogue"]),
        ("Roundtables", ["ROUNDTABLE", "ROUND TABLE"]),
        ("Committee of the Whole", ["COMMITTEE OF THE WHOLE"])
    ]

    for group, pattern_list in patterns:
        for pat in pattern_list:
            match = df["heading_clean"].str.contains(pat, case=False, regex=True) & df["neg_group"].isna()
            df.loc[match, "neg_group"] = group

    # Specific match for INC group with date 1995
    if "date" in df.columns:
        inc_match = df["heading_clean"].str.contains("WORKING GROUP", case=False, na=False) & \
                    df["date"].astype(str).str.contains("1995", na=False) & \
                    df["neg_group"].isna()
        df.loc[inc_match, "neg_group"] = "INC"

    df["neg_group"] = df["neg_group"].fillna("Other/None/Unknown")
    return df

interventions = classify_neg_group(interventions)
interactions = classify_neg_group(interactions)

# Define topic keyword classification
keywords = {
    "mitigation": ["mitigation", "reduction", "commitment", "pledges", "ndc", "nationally determined", "QELRO", "NAMA", "nationally appropriate mitigation actions", "policies and measures", "sectoral approaches", "P&Ms", "brazilian proposal", "proposal by brazil", "non-market", "Clarification of the Text in Section G", "time frames", "harvested wood products", "greenhouse gas-emitting energy", "sectors and source", "numbers", "hydrofluorocarbons"],
    "markets": ["markets", "market-based", "mechanism", "trading", "cdm", "joint implementation", "AAUs", "assigned amount", "transaction", "cooperative approaches", "Market and non-market", "6.2", "6.4", "AIJ", "activities implemented jointly", "HFC-23", "CCS", "storage", "single project", "baseline"],
    "aviation_maritime": ["aviation", "maritime", "bunker"],
    "forests": ["lulucf", "redd", "deforestation", "land use", "forestry"],
    "agriculture": ["agriculture"],
    "adaptation": ["adaptation"],
    "loss_and_damage": ["loss and damage", "loss-and-damage"],
    "response_measures": ["response measures", "adverse effects", "adverse impacts", "potential consequences", "3.14"],
    "finance": ["finance", "financial", "financing", "fund", "facility", "GEF"],
    "capacity_building": ["capacity"],
    "technology_transfer": ["technology", "transfer", "technologies"],
    "reporting_and_review": ["reporting", "inventor", "iar ", "International Assessment and Review", "communications", "transparency", "Consultative Group of Experts", "CGE", "International Transaction Log", "data interface", "metrics", "articles 5", "biennial update reports", "registry", "ICA process", "MRV", "accounting", "4.1", "Global Stocktake"],
    "compliance": ["compliance"],
    "science": ["science", "research", "ipcc", "intergovernmental panel", "socio-economic"],
    "arrangements_meetings": ["ARRANGEMENTS FOR INTERGOVERNMENTAL MEETINGS", "arrangements for COP"],
    "institutional_procedures": ["procedures", "procedural", "institutional matters", "institutional arrangements"],
    "organisation": ["organizational"],
    "country_specific": ["LDC", "Croatia", "Economies in Transition", "Kazakhstan", "Malta", "Russian proposal", "Proposal by the Russian", "Proposal from the Russian", "CACAM", "special circumstances", "process of transition"],
    "social_issues": ["gender", "indigenous"],
    "legal_issues": ["legal matters", "legal issues", "legal options"],
    "new_instrument": ["legal instrument"],
    "plenaries": ["plenary", "statements", "welcoming ceremony", "opening ceremony", "high-level segment"]
}

# Add keyword flags and topic sums
def add_topic_flags(df):
    for key, terms in keywords.items():
        pattern = "|".join(terms)
        df[key] = df["heading_clean"].str.contains(pattern, case=False, regex=True).astype(int)
        if key == "mitigation":
            df.loc[df["heading_clean"].str.contains("risk|finance commitments", case=False, na=False), key] = 0
        if key == "reporting_and_review":
            df.loc[df["heading_clean"].str.contains("4.10", case=False, na=False), key] = 0
    df["neg_topic_sum"] = df[[k for k in keywords.keys()]].sum(axis=1)
    df["other_unknown"] = (df["neg_topic_sum"] == 0).astype(int)
    return df

interventions = add_topic_flags(interventions)
interactions = add_topic_flags(interactions)

# Save output
interventions.to_csv("data/interventions_wtopics.csv", index=False)
interactions.to_csv("data/interactions_wtopics.csv", index=False)
