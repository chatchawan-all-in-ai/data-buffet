# curated_derp

2 cards in BigQuery dataset `curated_derp`.

# Tables

* [curated_invoice_line_cost](curated_invoice_line_cost.md) - One row = one MAC5 document line (per salesperson row) of a document with a matched posted DERP journal, carrying the DERP cost allocated to it, plus NO_LINE rows for journal cost that no line accounts for.
* [curated_journal_invoice](curated_journal_invoice.md) - One row = one DERP inventory movement journal (name IM-MAC-01) with the MAC5 document number parsed from its description and the match status against curated_mih, unique on journalNumber.
