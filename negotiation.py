import anthropic
import json

client = anthropic.Anthropic(api_key="your-api-key-here")


SELLER_CONTRACT = {
    "publisher": "Immediate Media",
    "available_segments": ["legal professionals", "financial decision makers", "C-suite executives"],
    "floor_cpm": 8.50,
    "brand_safety_exclusions": ["gambling", "alcohol", "payday loans"],
    "placement_rules": ["above the fold only", "no auto-play video"],
    "max_frequency_cap": 3,
    "guaranteed_viewability": 0.70
}

BUYER_CONTRACT = {
    "advertiser": "LexCorp Legal Software",
    "target_segments": ["legal professionals", "financial decision makers"],
    "max_cpm": 11.00,
    "required_viewability": 0.65,
    "brand_adjacency_exclusions": ["gambling", "adult content"],
    "preferred_placements": ["above the fold"],
    "impression_goal": 500000,
    "frequency_cap_required": 4
}

tools = [
    {
        "name": "make_offer",
        "description": "Make a deal offer to the other party.",
        "input_schema": {
            "type": "object",
            "properties": {
                "proposed_cpm": {"type": "number"},
                "segments": {"type": "array", "items": {"type": "string"}},
                "placement": {"type": "string"},
                "conditions": {"type": "array", "items": {"type": "string"}},
                "reasoning": {"type": "string"}
            },
            "required": ["proposed_cpm", "segments", "placement", "conditions", "reasoning"]
        }
    },
    {
        "name": "flag_mismatch",
        "description": "Flag a mismatch between what is offered and what is required.",
        "input_schema": {
            "type": "object",
            "properties": {
                "constraint_type": {"type": "string"},
                "detail": {"type": "string"},
                "dealbreaker": {"type": "boolean"}
            },
            "required": ["constraint_type", "detail", "dealbreaker"]
        }
    },
    {
        "name": "accept_deal",
        "description": "Accept the current offer and flag for human sign-off.",
        "input_schema": {
            "type": "object",
            "properties": {
                "final_cpm": {"type": "number"},
                "final_segments": {"type": "array", "items": {"type": "string"}},
                "final_placement": {"type": "string"},
                "final_conditions": {"type": "array", "items": {"type": "string"}},
                "deal_summary": {"type": "string"}
            },
            "required": ["final_cpm", "final_segments", "final_placement", "final_conditions", "deal_summary"]
        }
    },
    {
        "name": "walk_away",
        "description": "End negotiation without a deal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "unresolved_constraints": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["reason", "unresolved_constraints"]
        }
    }
]

def print_divider(label=""):
    if label:
        print(f"\n{'='*20} {label} {'='*20}")
    else:
        print(f"\n{'='*60}")

def call_agent(system_prompt, user_message):
    messages = [{"role": "user", "content": user_message}]
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        tools=tools,
        system=system_prompt,
        messages=messages
    )
    tool_call = None
    for block in response.content:
        if block.type == "tool_use":
            tool_call = block
            break
    return tool_call

def human_review(deal):
    print_divider("HUMAN SIGN-OFF REQUIRED")
    print(f"\n  Advertiser:  {BUYER_CONTRACT['advertiser']}")
    print(f"  Publisher:   {SELLER_CONTRACT['publisher']}")
    print(f"  CPM:         ${deal['final_cpm']:.2f}")
    print(f"  Segments:    {', '.join(deal['final_segments'])}")
    print(f"  Placement:   {deal['final_placement']}")
    print(f"  Conditions:  {', '.join(deal['final_conditions'])}")
    print(f"\n  Summary: {deal['deal_summary']}")
    est_spend = deal['final_cpm'] * BUYER_CONTRACT['impression_goal'] / 1000
    print(f"\n  Impression goal: {BUYER_CONTRACT['impression_goal']:,}")
    print(f"  Estimated spend: ${est_spend:,.2f}")
    while True:
        decision = input("\n  Approve this deal? (approve / reject / renegotiate): ").strip().lower()
        if decision in ["approve", "reject", "renegotiate"]:
            return decision
        print("  Please type: approve, reject, or renegotiate")

def handle_human_decision(decision):
    if decision == "approve":
        print_divider("DEAL APPROVED")
        print("\nDeal confirmed. Campaign will proceed to activation.")
    elif decision == "reject":
        print_divider("DEAL REJECTED")
        print("\nDeal rejected by human reviewer. No campaign will proceed.")
    elif decision == "renegotiate":
        print_divider("SENT BACK FOR RENEGOTIATION")
        print("\nHuman reviewer has requested renegotiation.")

def run_negotiation():
    print_divider("AD DEAL NEGOTIATION AGENT")
    print("\nData contracts loaded. Negotiation beginning.\n")

    print("SELLER CONTRACT (Immediate Media):")
    print(f"  Floor CPM:       ${SELLER_CONTRACT['floor_cpm']}")
    print(f"  Segments:        {', '.join(SELLER_CONTRACT['available_segments'])}")
    print(f"  Exclusions:      {', '.join(SELLER_CONTRACT['brand_safety_exclusions'])}")
    print(f"  Placement rules: {', '.join(SELLER_CONTRACT['placement_rules'])}")
    print(f"  Frequency cap:   {SELLER_CONTRACT['max_frequency_cap']}")
    print(f"  Viewability:     {SELLER_CONTRACT['guaranteed_viewability']}")

    print("\nBUYER CONTRACT (LexCorp Legal Software):")
    print(f"  Max CPM:         ${BUYER_CONTRACT['max_cpm']}")
    print(f"  Target segments: {', '.join(BUYER_CONTRACT['target_segments'])}")
    print(f"  Exclusions:      {', '.join(BUYER_CONTRACT['brand_adjacency_exclusions'])}")
    print(f"  Viewability req: {BUYER_CONTRACT['required_viewability']}")
    print(f"  Frequency cap:   {BUYER_CONTRACT['frequency_cap_required']}")
    print(f"  Impression goal: {BUYER_CONTRACT['impression_goal']:,}")

    seller_system = f"""You are a seller agent representing {SELLER_CONTRACT['publisher']}.
Your contract: {json.dumps(SELLER_CONTRACT)}.
Negotiate a programmatic ad deal. Use tools to make offers, flag mismatches, accept deals, or walk away.
Hard constraints: floor CPM ${SELLER_CONTRACT['floor_cpm']}, brand safety exclusions, placement rules.
You may negotiate on segments and minor conditions. Be commercial and concise.
Always use a tool — never respond with plain text."""

    buyer_system = f"""You are a buyer agent representing {BUYER_CONTRACT['advertiser']}.
Your contract: {json.dumps(BUYER_CONTRACT)}.
Negotiate a programmatic ad deal. Use tools to make offers, flag mismatches, accept deals, or walk away.
Hard constraints: max CPM ${BUYER_CONTRACT['max_cpm']}, required segments, viewability minimum.
You may negotiate on conditions. Be commercial and concise.
Always use a tool — never respond with plain text."""

    negotiation_log = []
    current_offer = None

    for round_num in range(1, 6):
        print_divider(f"ROUND {round_num}")

        # Build seller context from log
        if round_num == 1:
            seller_prompt = f"Begin negotiation. Buyer contract: {json.dumps(BUYER_CONTRACT)}. Make your opening offer using the make_offer tool."
        else:
            seller_prompt = f"Negotiation history so far: {json.dumps(negotiation_log)}. Buyer's last move: {json.dumps(current_offer)}. Respond using a tool."

        print("\n[SELLER AGENT thinking...]\n")
        seller_tool = call_agent(seller_system, seller_prompt)

        if not seller_tool:
            print("Seller gave no tool response. Ending.")
            break

        print(f"Seller action: {seller_tool.name}")
        for k, v in seller_tool.input.items():
            print(f"  {k}: {v}")

        negotiation_log.append({"round": round_num, "party": "seller", "action": seller_tool.name, "terms": seller_tool.input})

        if seller_tool.name == "walk_away":
            print(f"\nSeller walked away.")
            print(f"Reason: {seller_tool.input['reason']}")
            print(f"Unresolved: {', '.join(seller_tool.input['unresolved_constraints'])}")
            print_divider("NO DEAL REACHED")
            return

        if seller_tool.name == "accept_deal":
            decision = human_review(seller_tool.input)
            handle_human_decision(decision)
            return

        current_offer = {"party": "seller", "action": seller_tool.name, "terms": seller_tool.input}

        # Build buyer context from log
        buyer_prompt = f"Negotiation history: {json.dumps(negotiation_log)}. Seller's last move: {seller_tool.name} with terms: {json.dumps(seller_tool.input)}. Your contract: {json.dumps(BUYER_CONTRACT)}. Respond using a tool."

        print("\n[BUYER AGENT thinking...]\n")
        buyer_tool = call_agent(buyer_system, buyer_prompt)

        if not buyer_tool:
            print("Buyer gave no tool response. Ending.")
            break

        print(f"Buyer action: {buyer_tool.name}")
        for k, v in buyer_tool.input.items():
            print(f"  {k}: {v}")

        negotiation_log.append({"round": round_num, "party": "buyer", "action": buyer_tool.name, "terms": buyer_tool.input})

        if buyer_tool.name == "walk_away":
            print(f"\nBuyer walked away.")
            print(f"Reason: {buyer_tool.input['reason']}")
            print(f"Unresolved: {', '.join(buyer_tool.input['unresolved_constraints'])}")
            print_divider("NO DEAL REACHED")
            return

        if buyer_tool.name == "accept_deal":
            decision = human_review(buyer_tool.input)
            handle_human_decision(decision)
            return

        current_offer = {"party": "buyer", "action": buyer_tool.name, "terms": buyer_tool.input}

    print_divider("MAX ROUNDS REACHED")
    print("Negotiation did not conclude within the round limit.")

run_negotiation()