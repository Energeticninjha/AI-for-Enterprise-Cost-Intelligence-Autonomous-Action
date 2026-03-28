def calculate_advanced_roi(logs):
    amount = 0.0
    exception_triggered = False
    
    for log in reversed(logs[-60:]):
        if log.get('agent_name') == 'ExceptionAgent':
            exception_triggered = True
            
        details = log.get('details', {})
        if isinstance(details, dict):
            if 'amount' in details and float(details['amount']) > 0:
                amount = max(amount, float(details['amount']))
            elif 'pr_data' in details and isinstance(details['pr_data'], dict) and 'amount' in details['pr_data']:
                amount = max(amount, float(details['pr_data']['amount']))
                
    if exception_triggered:
        time_saved = "92%"
        # Cost Savings = (18% GST Penalty Avoided) + (₹2,500 Manual Labor Saved) + Consolidation
        cost = (0.18 * amount) + 2500 + 285000
        cost_str = f"₹{cost:,.0f}"
        delta_time = "Manual Labor Saved ⬆️"
        delta_cost = "18% GST + CapEx Consolidation ⬆️"
    else:
        time_saved = "65%"
        cost_str = f"₹1,500"
        delta_time = "Operational Efficiency ⬆️"
        delta_cost = "Standard Fast Track ⬆️"
        
    return time_saved, cost_str, delta_time, delta_cost
