from collections import defaultdict

def summarize_buyers(buyers_list, group_by="email"):
    buyer_count = defaultdict(int)
    for b in buyers_list:
        key = b[group_by]
        buyer_count[key] += 1
    return [{"buyer": k, "purchase_count": v} for k, v in buyer_count.items()]
