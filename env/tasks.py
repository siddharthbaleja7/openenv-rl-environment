from enum import Enum

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

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
    }
}
