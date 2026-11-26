"""
Lab 7 Module 2: Deterministic Budget Arithmetic & Bounded Iteration
モジュール 2：確定的予算計算と反復上限制御
"""
from typing import Any, Callable, Dict, List, Optional


def compute_budget_summary(items: List[Dict[str, Any]], budget_limit_yen: int) -> Dict[str, Any]:
    """
    TODO [Task 2.1]: Deterministic Budget Arithmetic (Week 5 Concept)
    Compute the budget in Python (never by the LLM), keeping confirmed and estimated costs apart.
    確定費用と見積費用を分けて、Pythonで予算を計算する。

    - budget_limit_yen must be a non-negative int, otherwise raise ValueError.
    - Each cost_yen must be a whole, non-negative number (not bool, not str), otherwise ValueError.
    - known_total_yen:     sum of items with is_estimate = False
    - estimated_total_yen: sum of items with is_estimate = True
    - projected_total_yen: known + estimated (the budget check uses this figure)
    - remaining_yen = budget_limit_yen - projected_total_yen
    - is_within_budget = projected_total_yen <= budget_limit_yen
    - has_estimates, item_count, items (name, cost_yen, is_estimate for each item)
    """
    # --- STUDENT IMPLEMENTATION START ---
    import math

    if type(budget_limit_yen) is not int or budget_limit_yen < 0:
        raise ValueError("budget_limit_yen must be a non-negative integer.")
    if not isinstance(items, list):
        raise ValueError("items must be a list.")

    normalized_items = []
    known_total = 0
    estimated_total = 0
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item {index} must be an object.")
        name = item.get("name")
        cost = item.get("cost_yen")
        is_estimate = item.get("is_estimate")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Item {index} must have a non-empty name.")
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            raise ValueError(f"Item {index} cost_yen must be a whole non-negative number.")
        if cost < 0 or (isinstance(cost, float) and (not math.isfinite(cost) or not cost.is_integer())):
            raise ValueError(f"Item {index} cost_yen must be a whole non-negative number.")
        if type(is_estimate) is not bool:
            raise ValueError(f"Item {index} is_estimate must be a boolean.")

        whole_cost = int(cost)
        normalized_items.append({
            "name": name.strip(),
            "cost_yen": whole_cost,
            "is_estimate": is_estimate,
        })
        if is_estimate:
            estimated_total += whole_cost
        else:
            known_total += whole_cost

    projected_total = known_total + estimated_total
    return {
        "known_total_yen": known_total,
        "estimated_total_yen": estimated_total,
        "projected_total_yen": projected_total,
        "remaining_yen": budget_limit_yen - projected_total,
        "is_within_budget": projected_total <= budget_limit_yen,
        "has_estimates": estimated_total > 0 or any(i["is_estimate"] for i in normalized_items),
        "item_count": len(normalized_items),
        "items": normalized_items,
    }
    # --- STUDENT IMPLEMENTATION END ---


ReviewFn = Callable[[str, int], bool]


def run_bounded_review(drafts: List[str], max_rounds: int = 3,
                       review_fn: Optional[ReviewFn] = None) -> Dict[str, Any]:
    """
    TODO [Task 2.2]: Bounded Review Iteration Ceiling (Week 6 StateGraph Concept)
    Run a draft -> review loop with a hard ceiling of `max_rounds`.
    レビューは最大 max_rounds 回まで。上限に達したら 'needs_attention'（偽の成功を報告しない）。

    drafts:    successive drafts (draft i is what the writer produces in round i)
    review_fn: review_fn(draft, round_number) -> True if approved.
               Default (None): only the last supplied draft is approved.

    - max_rounds < 1 (or not an int) -> raise ValueError
    - Call review_fn at most max_rounds times, stop at the first approval.
    - Approved     -> status "completed", rounds_executed = that round, final_draft = that draft
    - Not approved -> status "needs_attention", final_draft = last reviewed draft ("" if none), add "reason"
    - Always return rounds_executed, max_rounds, status, final_draft and
      history = [{"round": n, "approved": bool}, ...]
    """
    # --- STUDENT IMPLEMENTATION START ---
    if type(max_rounds) is not int or max_rounds < 1:
        raise ValueError("max_rounds must be a positive integer.")
    if not isinstance(drafts, list):
        raise ValueError("drafts must be a list.")

    reviewer = review_fn if review_fn is not None else (
        lambda _draft, round_number: round_number == len(drafts)
    )
    history = []
    final_draft = ""
    rounds_executed = 0
    status = "needs_attention"
    for round_number, draft in enumerate(drafts[:max_rounds], start=1):
        rounds_executed += 1
        final_draft = draft if isinstance(draft, str) else ""
        reviewer_approved = bool(reviewer(draft, round_number))
        has_draft = isinstance(draft, str) and bool(draft.strip())
        approved = reviewer_approved and has_draft
        history.append({"round": round_number, "approved": approved})
        if approved:
            status = "completed"
            break

    result = {
        "rounds_executed": rounds_executed,
        "max_rounds": max_rounds,
        "status": status,
        "final_draft": final_draft,
        "history": history,
    }
    if status != "completed":
        result["reason"] = (
            "No drafts were provided."
            if not drafts
            else "The review limit was reached without approval or no non-empty draft was approved."
        )
    return result
    # --- STUDENT IMPLEMENTATION END ---
