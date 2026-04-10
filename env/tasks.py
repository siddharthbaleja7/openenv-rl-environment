from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Difficulty notes used by docs and validator tooling.
TASK_DIFFICULTY_NOTES = {
    "task_easy_1": {
        "difficulty": Difficulty.EASY.value,
        "why_harder_than_previous": "Baseline task. No prerequisite task.",
        "state_space_notes": "Single refund intent with low ambiguity.",
        "typical_horizon": 3,
        "stochasticity": "Low",
        "expected_optimal_score": 0.99,
    },
    "task_medium_1": {
        "difficulty": Difficulty.MEDIUM.value,
        "why_harder_than_previous": "Requires rejecting a tempting but policy-violating refund.",
        "state_space_notes": "Adds policy conflict and negative-action trap (refund penalty).",
        "typical_horizon": 3,
        "stochasticity": "Low",
        "expected_optimal_score": 0.99,
    },
    "task_hard_1": {
        "difficulty": Difficulty.HARD.value,
        "why_harder_than_previous": "Requires data fetch + correct escalation reason + customer communication.",
        "state_space_notes": "More branching paths and larger failure surface due to ordering constraints.",
        "typical_horizon": 3,
        "stochasticity": "Medium",
        "expected_optimal_score": 0.99,
    },
    "task_fraud_detection": {
        "difficulty": Difficulty.HARD.value,
        "why_harder_than_previous": "Introduces chargeback-history risk and high-value refund denial logic.",
        "state_space_notes": "Adds fraud/risk state and denial behavior under customer pressure.",
        "typical_horizon": 4,
        "stochasticity": "Medium",
        "expected_optimal_score": 0.99,
    },
}

TASKS = {
    "task_easy_1": {
        "difficulty": Difficulty.EASY.value,
        "ticket": {
            "ticket_id": "TKT-1001",
            "user_id": "USR-A1",
            "issue_type": "refund_request",
            "subject": "Accidental purchase",
            "body": "I clicked buy by mistake on the Premium plan today. Can I get a refund?",
            "status": "open"
        },
        "user_data": {
            "user_id": "USR-A1",
            "account_tier": "premium",
            "join_date": "2023-01-15"
        },
        "policy": {
            "refund_request": "If requested within 7 days of accidental purchase, issue full refund."
        }
    },
    "task_medium_1": {
        "difficulty": Difficulty.MEDIUM.value,
        "ticket": {
            "ticket_id": "TKT-2002",
            "user_id": "USR-B2",
            "issue_type": "refund_request",
            "subject": "Refund for last year",
            "body": "I didn't use my account much last year, please refund the annual fee.",
            "status": "open"
        },
        "user_data": {
            "user_id": "USR-B2",
            "account_tier": "standard",
            "join_date": "2021-05-20"
        },
        "policy": {
            "refund_request": "Strictly no refunds for unused time from previous billing cycles. Explain policy and close ticket."
        }
    },
    "task_hard_1": {
        "difficulty": Difficulty.HARD.value,
        "ticket": {
            "ticket_id": "TKT-3003",
            "user_id": "USR-C3",
            "issue_type": "billing_discrepancy",
            "subject": "Double charged again!",
            "body": "This is the third month in a row I've been charged twice! Fix this or I'm leaving.",
            "status": "open"
        },
        "user_data": {
            "user_id": "USR-C3",
            "account_tier": "enterprise",
            "join_date": "2019-11-01"
        },
        "policy": {
            "billing_discrepancy": "For enterprise clients with recurring double charges, fetch user data, escalate immediately to billing_tier2, and reply to customer apologizing for the delay."
        }
    },
    "task_fraud_detection": {
        "difficulty": Difficulty.HARD.value,
        "ticket": {
            "ticket_id": "TKT-4004",
            "user_id": "USR-C3",
            "issue_type": "refund_request",
            "subject": "Refund for high-value transaction",
            "body": "I was charged $500 for a service I didn’t use. Please refund immediately.",
            "status": "open"
        },
        "user_data": {
            "user_id": "USR-C3",
            "account_tier": "standard",
            "join_date": "2020-11-11",
            "chargeback_history": 3
        },
        "policy": {
            "refund_request": "High-value refunds require no history of chargebacks. Reject politely if chargebacks exist."
        }
    }
}
