import math

def parse_ratio(val_str):
    """
    Safely parses complex inputs including decimals, fractions, 
    and decimal fractions (e.g., '1.55', '31/20', '1.5/1', '330/1').
    """
    val_str = val_str.strip()
    if not val_str: 
        return 0.0
    if "/" in val_str:
        try:
            parts = val_str.split("/")
            if len(parts) == 2:
                numerator = float(parts[0])
                denominator = float(parts[1])
                if denominator != 0:
                    return numerator / denominator
        except: 
            return 0.0
    try: 
        return float(val_str)
    except: 
        return 0.0

def find_best_bulk_v2(cost_val, return_val):
    """
    Simultaneously monitors per-unit cost and per-unit return,
    finding the lowest item batch scale count (item_count) such that:
    1. Total procurement cost (item_count * cost_val) closely targets an integer.
    2. Total transaction return (item_count * return_val) closely targets an integer.
    """
    if cost_val <= 0 or return_val <= 0:
        return 1, 1, 1
        
    best_diff = float('inf')
    best_items = 1
    best_total_cost = 1
    best_total_return = 1
    
    # Large window iteration loop up to 200 items to fit asymmetric fraction pairs
    for item_count in range(1, 201):
        cost_exact = item_count * cost_val
        return_exact = item_count * return_val
        
        cost_round = round(cost_exact)
        return_round = round(return_exact)
        
        if cost_round == 0 or return_round == 0:
            continue
            
        diff_cost = abs(cost_exact - cost_round)
        diff_return = abs(return_exact - return_round)
        total_diff = diff_cost + diff_return  # Sum of error margins across both vectors
        
        # Immediate clean exit on finding absolute integer match within tolerance threshold
        if total_diff < 1e-4:
            return item_count, cost_round, return_round
            
        if total_diff < best_diff:
            best_diff = total_diff
            best_items = item_count
            best_total_cost = cost_round
            best_total_return = return_round
            
    return best_items, best_total_cost, best_total_return


def run_arbitrage_calc(mode, d_to_e, gold_d, gold_e, cost, return_val, gold_item):
    """
    Core mathematical engine executing arbitrage tracking matrices.
    Intercepts and rounds off floating point fractions to fit pure integer-only bulk listing boundaries.
    """
    if d_to_e <= 0 or return_val <= 0 or cost <= 0:
        return None

    log_lines = []
    log_lines.append("="*45)
    log_lines.append(f"🔄 触发核心套利计算 [模式: {mode}]")
    
    # Calculate optimal bulk quantity parameters matching real trade market constraints
    items_to_sell, total_cost_token, total_return_token = find_best_bulk_v2(cost, return_val)
    
    if mode == "E买D卖":
        log_lines.append(f"输入状态 -> 1D={d_to_e}E | 买入价={cost:.4f}E | 卖出价={return_val:.4f}D")
        log_lines.append(f"[步骤1] 推荐整单规模: 批量买入 {items_to_sell} 件共需支付 {total_cost_token} E")
        
        total_e_paid = total_cost_token
        d_to_receive = total_return_token
        
        # Calculate aggregate gold sink tax metrics against smoothed matching integers
        gold_item_total = items_to_sell * gold_item
        gold_e_total = total_e_paid * gold_e
        gold_d_total = d_to_receive * gold_d
        gold_per_round = gold_item_total + gold_e_total + gold_d_total
        
        log_lines.append(f"[步骤2] 单轮挂单金币明细:")
        log_lines.append(f"        - 标的税({items_to_sell}件): {gold_item_total:,.0f}")
        log_lines.append(f"        - 支出E税({total_e_paid}E): {gold_e_total:,.0f}")
        log_lines.append(f"        - 收入D税({d_to_receive}D): {gold_d_total:,.0f}")
        log_lines.append(f"        - 单轮市集总共吃金币: {gold_per_round:,.0f}")

        # Conversion accounting execution
        cost_in_d = total_e_paid / d_to_e
        net_profit_d = d_to_receive - cost_in_d
        roi = (net_profit_d / cost_in_d) * 100 if cost_in_d > 0 else 0
        
        log_lines.append(f"[步骤3] 单轮财务转化:")
        log_lines.append(f"        - 成本折合: {cost_in_d:.4f} D | 实收总价: {d_to_receive} D")
        log_lines.append(f"        - 单轮净赚: {net_profit_d:+.4f} D | 预估 ROI: {roi:+.2f}%")
        
        if net_profit_d <= 0:
            log_lines.append("[警告] 该组合当前为负收益。")
            return {"roi": roi, "gold": float('inf'), "details": "⚠️ 当前价格属于亏本套利", "logs": "\n".join(log_lines)}
            
        scale_to_one_d = 1.0 / net_profit_d
        gold_spent_per_d = gold_per_round * scale_to_one_d
        
        rec_str = (
            f"💡 【市集最优挂单推荐】:\n"
            f"  👉 目标动作: 一次性扫货上架 {items_to_sell} 个物品\n"
            f"  👉 进货预备: 准备整数本金 {total_e_paid} 个 崇高石 (E)\n"
            f"  👉 市集定价: 设置总出货价 {d_to_receive} 个 Divine (D)"
        )
        
    else:
        # D买E卖 Mode Pipeline
        log_lines.append(f"输入状态 -> 1D={d_to_e}E | 买入价={cost:.4f}D | 卖出价={return_val:.4f}E")
        log_lines.append(f"[步骤1] 推荐整单规模: 批量买入 {items_to_sell} 件共需支付 {total_cost_token} D")
        
        total_d_paid = total_cost_token
        e_to_receive = total_return_token
        
        # Calculate aggregate gold sink tax metrics
        gold_item_total = items_to_sell * gold_item
        gold_d_total = total_d_paid * gold_d
        gold_e_total = e_to_receive * gold_e
        gold_per_round = gold_item_total + gold_d_total + gold_e_total
        
        log_lines.append(f"[步骤2] 单轮挂单金币明细:")
        log_lines.append(f"        - 标的税: {gold_item_total:,.0f} | 支出D税: {gold_d_total:,.0f} | 收入E税: {gold_e_total:,.0f}")
        log_lines.append(f"        - 单轮总计扣除: {gold_per_round:,.0f}")

        cost_in_e = total_d_paid * d_to_e
        net_profit_e = e_to_receive - cost_in_e
        roi = (net_profit_e / cost_in_e) * 100 if cost_in_e > 0 else 0
        
        log_lines.append(f"[步骤3] 单轮财务转化 (E基准):")
        log_lines.append(f"        - 成本折合: {cost_in_e:.4f} E | 实收: {e_to_receive} E | 净赚: {net_profit_e:+.4f} E")
        
        if net_profit_e <= 0:
            log_lines.append("[警告] 负收益套利。")
            return {"roi": roi, "gold": float('inf'), "details": "⚠️ 当前价格属于亏本套利", "logs": "\n".join(log_lines)}
            
        scale_to_one_d = (1.0 / net_profit_e) * d_to_e
        gold_spent_per_d = gold_per_round * scale_to_one_d

        rec_str = (
            f"💡 【市集最优挂单推荐】:\n"
            f"  👉 目标动作: 一次性扫货上架 {items_to_sell} 个物品\n"
            f"  👉 进货预备: 准备整数本金 {total_d_paid} 个 Divine (D)\n"
            f"  👉 市集定价: 设置总出货价 {e_to_receive} 个 崇高石 (E)"
        )
        
    log_lines.append("="*45)
    return {"roi": roi, "gold": gold_spent_per_d, "details": rec_str, "logs": "\n".join(log_lines)}