from __future__ import annotations
from dataclasses import dataclass
from .detectors import detect_all
from .models import PIIType

@dataclass(frozen=True)
class Gold:
    text: str
    pii_type: PIIType | None  # None = explicitly negative candidate

BENCHMARK = [
    ("Contact Person: Aarav Mehta", [Gold("Aarav Mehta", PIIType.PERSON)]),
    ("Email: rashi.patil@example.com", [Gold("rashi.patil@example.com", PIIType.EMAIL)]),
    ("Telephone: +91 98765 43210", [Gold("+91 98765 43210", PIIType.PHONE)]),
    ("Company: Meridian Technologies Private Limited", [Gold("Meridian Technologies Private Limited", PIIType.ORGANIZATION)]),
    ("Registered Office: 12 Industrial Road, Sector 4, Pune – 411001, Maharashtra, India", [Gold("12 Industrial Road, Sector 4, Pune – 411001, Maharashtra, India", PIIType.ADDRESS)]),
    ("SSN: 123-45-6789", [Gold("123-45-6789", PIIType.SSN)]),
    ("Card: 4111 1111 1111 1111", [Gold("4111 1111 1111 1111", PIIType.CREDIT_CARD)]),
    ("Date of Birth: 19 July 2004", [Gold("19 July 2004", PIIType.DOB)]),
    ("Server IP: 192.0.2.44", [Gold("192.0.2.44", PIIType.IP_ADDRESS)]),
    ("Order 123456 is ready.", [Gold("123456", None)]),
    ("The offer closes on December 18, 2025.", [Gold("December 18, 2025", None)]),
    ("CIN U28129PN1979PLC141032 is public corporate information.", [Gold("U28129PN1979PLC141032", None)]),
    ("Amount: ₹7,100.00 million", [Gold("₹7,100.00", None)]),
    ("Website: www.example.com", [Gold("www.example.com", None)]),
]


def evaluate_benchmark():
    per_type={t.value:{"tp":0,"fp":0,"fn":0} for t in PIIType}
    total_tp=total_fp=total_fn=0
    negative_total=negative_correct=0

    for text,golds in BENCHMARK:
        detections=detect_all(text)
        for gold in golds:
            matches=[d for d in detections if not (d.end <= text.find(gold.text) or d.start >= text.find(gold.text)+len(gold.text))]
            if gold.pii_type is None:
                negative_total += 1
                negative_correct += 0 if matches else 1
                if matches:
                    total_fp += 1
            else:
                matched=next((d for d in matches if d.pii_type==gold.pii_type),None)
                if matched:
                    per_type[gold.pii_type.value]["tp"]+=1; total_tp+=1
                else:
                    per_type[gold.pii_type.value]["fn"]+=1; total_fn+=1
        # Any detection that doesn't overlap a positive gold span is a false positive.
        positive_spans=[(text.find(g.text),text.find(g.text)+len(g.text),g.pii_type) for g in golds if g.pii_type]
        for d in detections:
            if not any(d.start < e and d.end > s and d.pii_type==t for s,e,t in positive_spans):
                if not any(g.pii_type is None and d.start < text.find(g.text)+len(g.text) and d.end > text.find(g.text) for g in golds):
                    per_type[d.pii_type.value]["fp"]+=1; total_fp+=1

    precision=total_tp/(total_tp+total_fp) if total_tp+total_fp else 0.0
    recall=total_tp/(total_tp+total_fn) if total_tp+total_fn else 0.0
    accuracy=(total_tp+negative_correct)/(total_tp+total_fn+negative_total) if (total_tp+total_fn+negative_total) else 0.0
    jaccard_iou=total_tp/(total_tp+total_fp+total_fn) if total_tp+total_fp+total_fn else 0.0
    for v in per_type.values():
        tp,fp,fn=v['tp'],v['fp'],v['fn']
        v['precision']=tp/(tp+fp) if tp+fp else 0.0
        v['recall']=tp/(tp+fn) if tp+fn else 0.0
        v['f1']=2*v['precision']*v['recall']/(v['precision']+v['recall']) if v['precision']+v['recall'] else 0.0
    return {"overall":{"tp":total_tp,"fp":total_fp,"fn":total_fn,"precision":precision,"recall":recall,"accuracy":accuracy,"jaccard_iou":jaccard_iou},"per_type":per_type,"negative_candidates":negative_total,"negative_correct":negative_correct}


def evaluate_rhp(doc_path: str, gt_path: str):
    import json
    import re
    from docx import Document
    from .document import iter_paragraphs, discover_entities
    from .detectors import merge_and_resolve
    from .models import Span
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        gt_data = json.load(f)
        
    gt_map = {item['paragraph_index']: item['annotations'] for item in gt_data}
    
    doc = Document(str(doc_path))
    registry = discover_entities(doc)
    
    per_type = {t.value: {"tp": 0, "fp": 0, "fn": 0} for t in PIIType}
    total_tp = total_fp = total_fn = 0
    negative_total = negative_correct = 0
    total_gold = 0
    total_pred = 0
    
    for i, p in enumerate(iter_paragraphs(doc)):
        if i not in gt_map:
            continue
            
        text = p.text or ""
        if not text:
            continue
            
        spans = []
        spans.extend(detect_all(text))
        for (type_name, lookup_string), canonical in registry.items():
            if type_name in {PIIType.PERSON.value, PIIType.ORGANIZATION.value}:
                pattern_parts = [re.escape(w) for w in lookup_string.split()]
                if not pattern_parts: continue
                if type_name == PIIType.PERSON.value:
                    pattern = r'\b' + r'\s+'.join(pattern_parts) + r'\b'
                else:
                    pattern = r'(?<![A-Za-z0-9])' + r'\s+'.join(pattern_parts) + r'(?![A-Za-z0-9])'
            else:
                pattern = re.escape(lookup_string)
            for match in re.finditer(pattern, text, re.I):
                spans.append(Span(match.start(), match.end(), match.group(), PIIType(type_name), 1.0, "entity-registry"))
        spans = merge_and_resolve(spans)
        
        golds = gt_map[i]
        total_gold += len(golds)
        total_pred += len(spans)
        
        gold_matched = set()
        pred_matched = set()
        
        for p_idx, pred in enumerate(spans):
            for g_idx, gold in enumerate(golds):
                if pred.start == gold['start'] and pred.end == gold['end'] and pred.pii_type.value == gold['type']:
                    gold_matched.add(g_idx)
                    pred_matched.add(p_idx)
                    
        for g_idx, gold in enumerate(golds):
            if gold['type'] is None:
                negative_total += 1
                # If any prediction overlaps this negative gold, it's a false positive on the negative
                overlapped = False
                for p_idx, pred in enumerate(spans):
                    if pred.start < gold['end'] and pred.end > gold['start']:
                        overlapped = True
                        break
                if not overlapped:
                    negative_correct += 1
                continue
                
            if g_idx in gold_matched:
                per_type[gold['type']]['tp'] += 1
                total_tp += 1
            else:
                per_type[gold['type']]['fn'] += 1
                total_fn += 1
                
        for p_idx, pred in enumerate(spans):
            if p_idx not in pred_matched:
                # Need to check if it overlapped an explicit negative? 
                # Actually, any prediction not exactly matching a positive gold is FP
                per_type[pred.pii_type.value]['fp'] += 1
                total_fp += 1
                
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    jaccard_iou = total_tp / (total_tp + total_fp + total_fn) if (total_tp + total_fp + total_fn) else 0.0
    accuracy = (total_tp + negative_correct) / (total_tp + total_fn + negative_total) if (total_tp + total_fn + negative_total) else 0.0
    
    for v in per_type.values():
        tp, fp, fn = v['tp'], v['fp'], v['fn']
        v['precision'] = tp / (tp + fp) if tp + fp else 0.0
        v['recall'] = tp / (tp + fn) if tp + fn else 0.0
        v['f1'] = 2 * v['precision'] * v['recall'] / (v['precision'] + v['recall']) if v['precision'] + v['recall'] else 0.0
        
    return {
        "overall": {
            "tp": total_tp, "fp": total_fp, "fn": total_fn, 
            "precision": precision, "recall": recall, "f1": f1,
            "jaccard_iou": jaccard_iou, "accuracy": accuracy
        },
        "per_type": per_type,
        "paragraphs_evaluated": len(gt_map),
        "total_gold": total_gold,
        "total_pred": total_pred,
        "negative_candidates": negative_total,
        "negative_correct": negative_correct
    }

def run_all_evaluations(doc_path: str, gt_path: str, out_path: str):
    import json
    bench = evaluate_benchmark()
    rhp = evaluate_rhp(doc_path, gt_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({"benchmark": bench, "rhp": rhp}, f, indent=2)
    return bench, rhp
