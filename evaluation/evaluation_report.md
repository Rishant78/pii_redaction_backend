# Evaluation Report

## A. Controlled synthetic benchmark

- **Dataset size**: 14 manually annotated short strings.
- **Clear statement**: This is a very small, highly controlled benchmark designed as a smoke-test to ensure all 9 PII detectors are functional. It should not be interpreted as a full-document production accuracy estimate.

| Metric | Result |
|---|---:|
| True positives | 9 |
| False positives | 0 |
| False negatives | 0 |
| Precision | 100.00% |
| Recall | 100.00% |
| Candidate-level accuracy | 100.00% |
| F1 | 100.00% |

### Synthetic Per-type results
| PII type | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| PERSON | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| EMAIL | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| PHONE | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| ORGANIZATION | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| ADDRESS | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| SSN | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| CREDIT_CARD | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| DOB | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| IP_ADDRESS | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |

## B. RHP manually annotated subset

This evaluation runs the full production two-pass pipeline (including the entity registry) over a standoff JSON ground truth subset of the actual Red Herring Prospectus. Matches are counted as True Positives **only if the paragraph index, start character offset, end character offset, and PII type match exactly**.

- **Number of paragraphs evaluated**: 7
- **Number of gold annotations**: 13
- **Overall Predictions**: 13
- **True Positives (TP)**: 13
- **False Positives (FP)**: 0
- **False Negatives (FN)**: 0
- **Overall Micro Precision**: 100.00%
- **Overall Micro Recall**: 100.00%
- **Overall Micro F1**: 100.00%

### RHP Per-type results
| PII type | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| PERSON | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| EMAIL | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| PHONE | 1 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| ORGANIZATION | 6 | 0 | 0 | 100.00% | 100.00% | 100.00% |
| ADDRESS | 4 | 0 | 0 | 100.00% | 100.00% | 100.00% |

*(Note: Candidate-level accuracy for the RHP is omitted because "True Negatives" cannot be objectively quantified at the span-offset level without assuming all ordinary document text is negative. We rely entirely on Precision, Recall, and F1.)*

## C. Limitations

- **Observed Types Only**: The RHP evaluation covers only the PII types actually observed in the document (PERSON, EMAIL, PHONE, ORGANIZATION, ADDRESS).
- **Missing Synthetic Types**: SSN, credit card, DOB and IP detection are validated separately through the synthetic benchmark tests because those types were not observed in the RHP document. Do not invent examples of these in the real ground truth.
- **Subset Only**: The RHP ground truth is a small manually annotated subset (7 paragraphs), not the entire 127-page document.
- **Not Full-Document Ground Truth**: Metrics therefore should not be presented as full-document ground truth performance, as complex prose and edge cases in unannotated paragraphs may produce false positives/negatives not captured here.
