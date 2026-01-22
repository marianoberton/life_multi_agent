from datetime import datetime, timedelta
from typing import Dict, Any
from backend.core.setup import supabase

class FinancialAnalytics:
    def __init__(self):
        pass

    def calculate_burn_rate(self) -> Dict[str, Any]:
        """
        Calculates the current month's burn rate and projected end-of-month spend.
        Returns:
            {
                "total_spent": float,
                "projected_end_month": float,
                "burn_rate_daily": float,
                "days_remaining": int
            }
        """
        now = datetime.now()
        start_of_month = now.replace(day=1).strftime("%Y-%m-%d")
        # Get next month's first day
        next_month = (now.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_of_month = (next_month - timedelta(days=1)).day
        
        current_day = now.day
        days_in_month = end_of_month
        days_remaining = days_in_month - current_day

        # Fetch all transactions for current month
        # Note: In a real production app, we would sum in SQL for efficiency.
        response = supabase.table("finance_transactions") \
            .select("amount") \
            .gte("date_transaction", start_of_month) \
            .lt("date_transaction", next_month.strftime("%Y-%m-%d")) \
            .execute()

        transactions = response.data
        total_spent = sum(t["amount"] for t in transactions) if transactions else 0.0

        if current_day > 0:
            burn_rate_daily = total_spent / current_day
        else:
            burn_rate_daily = 0.0

        projected_spend = total_spent + (burn_rate_daily * days_remaining)

        return {
            "total_spent": round(total_spent, 2),
            "projected_end_month": round(projected_spend, 2),
            "burn_rate_daily": round(burn_rate_daily, 2),
            "days_remaining": days_remaining
        }
