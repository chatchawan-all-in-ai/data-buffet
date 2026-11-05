---
type: BigQuery Table
title: "tbcontact"
description: "One row = one CRM contact (per company), unique on (company_id, id)."
resource: "https://console.cloud.google.com/bigquery?project=databuffet-nonprd&p=databuffet-nonprd&d=validated_mac5&t=tbcontact&page=table"
project_id: databuffet-nonprd
dataset_id: validated_mac5
table_id: tbcontact
tags: ["validated", "validated_mac5", "mac5", "validated_full"]
sources:
  - id: sqlx
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/definitions/validated/mac5/tbcontact.sqlx"
    title: "Dataform definition (validated/mac5/tbcontact.sqlx)"
  - id: wiki
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/validated-layer.md"
    title: "Data Mart wiki (document/project_wiki/validated/validated-layer.md)"
  - id: inventory
    resource: "https://github.com/ALL-IN-AI-ASIA/data-buffet/blob/dev/document/project_wiki/validated/source-inventory.md"
    title: "Data Mart wiki: validated source inventory"
generated: { by: "agent:claude-code/claude-sonnet-5-5", at: "2026-11-05T21:55:28+07:00" }
status: draft
---

# What it is

Validated copy of MAC5 `tbcontact`: every column is trimmed/cast with the shared helpers, the extract date is standardised to `asatdate`, and duplicates are collapsed. There is no business logic at this layer. Table meaning: CRM contacts of customers and projects: name, address parts, role, segment, status colour and personal profile fields.
No other repo object reads it.

# Grain and key

One row per `company_id`, `id`. The key is declared twice in the definition (`uniqueKey` and `pk_key`) and enforced as a `NOT ENFORCED` primary key after full builds.

# Schema

| Column | Type | Description |
|---|---|---|
| `company_id` | STRING | Company code; always `ag01` (the table is loaded from the ag01 database only). |
| `id` | STRING | Contact ID (e.g. `CT`- or `AC`-prefixed code with a suffix). |
| `contactpersonal` | STRING | Contact kind code (1 = individual, 2 = juristic person). |
| `contactcompany` | STRING | Company code the contact belongs to (0 = none). |
| `contactcop` | STRING | Legal entity type of the contact in Thai (individual or juristic person). |
| `contactsegment` | STRING | Customer segment code of the contact (e.g. PV, CT, DV, GV, TT). |
| `contactchannel` | STRING | Sales channel of the contact (e.g. SCG Homemart, SCG HomeSolution). |
| `contactstatus` | STRING | Status colour of the contact in Thai (yellow, red or green). |
| `contacttitle` | STRING | Name title of the contact (e.g. Khun). |
| `contactname` | STRING | Full name of the contact. |
| `contactnick` | STRING | Nickname of the contact. |
| `contactaddress` | STRING | Street address of the contact. |
| `contactaddress1` | STRING | Province of the contact's address. |
| `contactaddress2` | STRING | District of the contact's address. |
| `contactaddress3` | STRING | Sub-district of the contact's address. |
| `contactaddress4` | STRING | Postal code of the contact's address. |
| `contactaddress5` | STRING | Country of the contact's address. |
| `contactaddress6` | STRING | Additional address line of the contact. |
| `contacttel` | STRING | Phone number of the contact. |
| `contactmail` | STRING | Email address of the contact. |
| `contacttype` | STRING | Contact type of the record. |
| `contactbday` | DATE | Birth date of the contact. |
| `contactage` | STRING | Age of the contact in years. |
| `contactbyear` | STRING | Birth year of the contact. |
| `contacthob` | STRING | Hobbies of the contact. |
| `contactstudy` | STRING | Education of the contact. |
| `contactmag` | STRING | Magazines the contact reads. |
| `contactme` | STRING | Personal note about the contact. |
| `contactcolor` | STRING | Favourite colour of the contact. |
| `contactfood` | STRING | Favourite food of the contact. |
| `contactlife` | STRING | Lifestyle of the contact. |
| `contactact` | STRING | Activities of the contact. |
| `contactsday` | STRING | Special day of the contact (e.g. anniversary). |
| `contactdesc` | STRING | Free-text description of the contact. |
| `contactlove` | STRING | Name of the contact's spouse or partner. |
| `contactson` | STRING | Number of children of the contact. |
| `contactcntson` | STRING | Number of sons of the contact. |
| `contactcntgirl` | STRING | Number of daughters of the contact. |
| `contactsonname1` | STRING | Name of child 1 of the contact. |
| `contactsonage1` | STRING | Age of child 1 of the contact. |
| `contactsonstudy1` | STRING | Education of child 1 of the contact. |
| `contactsonname2` | STRING | Name of child 2 of the contact. |
| `contactsonage2` | STRING | Age of child 2 of the contact. |
| `contactsonstudy2` | STRING | Education of child 2 of the contact. |
| `contactsonname3` | STRING | Name of child 3 of the contact. |
| `contactsonage3` | STRING | Age of child 3 of the contact. |
| `contactsonstudy3` | STRING | Education of child 3 of the contact. |
| `contactposition` | STRING | Role of the contact in Thai (e.g. goods receiver, project owner, engineer, contractor). |
| `contactpower` | STRING | Decision-power flag of the contact (`Yes` or `No`). |
| `projectcode` | STRING | Project code the contact is linked to. |
| `contactpp1` | STRING | Additional profile field 1 of the contact. |
| `contactpp2` | STRING | Additional profile field 2 of the contact. |
| `contactpp3` | STRING | Additional profile field 3 of the contact. |
| `contactpp4` | STRING | Additional profile field 4 of the contact. |
| `contactpp5` | STRING | Additional profile field 5 of the contact. |
| `contactpp6` | STRING | Additional profile field 6 of the contact. |
| `insertby` | STRING | User code of the person who created the record. |
| `insertwhen` | STRING | Date and time the record was created, as text. |
| `lastupdate` | STRING | Date and time the record was last updated, as text. |
| `contactpath20` | STRING | File path of an attachment of the contact. |
| `contactdebcode` | STRING | MAC5 customer code linked to the contact (joins `deb.debcode`). |
| `activestatus` | INT64 | Active flag of the contact (1 = active). |
| `lineidcorp` | STRING | Corporate LINE ID of the contact. |

# How it is built

- Definition: `definitions/validated/mac5/tbcontact.sqlx` (`type: "table"`, tags `validated`, `validated_full`).
- Reads: [raw_mac5_ag01.tbcontact](/initial/raw_mac5_ag01/tbcontact.md).
- **Full rebuild** (`type: "table"`) on every run from all raw partitions.
- Dedup: `QUALIFY ROW_NUMBER() OVER(PARTITION BY <key> ORDER BY contactname desc, contactdesc desc) = 1`.
- Storage: not partitioned; cluster by `company_id`, `id`.

# Examples

Sample recent rows:

```sql
SELECT *
FROM `databuffet-nonprd.validated_mac5.tbcontact`
LIMIT 100
```

Duplicate keys:

```sql
SELECT company_id, id, COUNT(*) AS n
FROM `databuffet-nonprd.validated_mac5.tbcontact`
GROUP BY company_id, id
HAVING n > 1
```
