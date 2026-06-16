# Ad Deal Negotiation Agent

A multi-agent system that simulates a programmatic advertising negotiation between a publisher and an advertiser, with a human sign-off requirement before any deal is confirmed.

## What it is

A multi-agent negotiation system built to explore how agentic AI handles structured commercial negotiation, constraint enforcement, and human oversight in a context that maps to a real and emerging problem in ad tech.

I built this after working through a simpler single-agent version that researched companies by browsing their websites. That project made the loop and tool-use mechanics click. This one is an attempt to apply those mechanics to something closer to a real commercial problem: agentic systems negotiating deals on behalf of publishers and advertisers, which is where a meaningful part of the ad tech industry appears to be heading.

## What it does

Two AI agents negotiate a programmatic ad deal in real time. Each agent has a defined data contract: a structured schema declaring their constraints, goals, and hard limits. The agents exchange offers, flag mismatches, propose compromises, and either reach a deal or walk away with a clear explanation of why.

When a deal is reached, the system pauses and presents the full terms to a human reviewer. The reviewer can approve, reject, or send the deal back for renegotiation. Nothing proceeds without explicit human sign-off.

## Why data contracts matter

In my view, one of the more interesting design challenges in this system is not the negotiation logic itself but the data contract that precedes it.

Before any negotiation begins, both sides must declare their constraints in a structured schema: floor price, audience segments, brand safety exclusions, placement rules, viewability requirements, frequency caps. The negotiation cannot start until both contracts are loaded.

This matters because mismatches between buyer and seller constraints are not always obvious. Without a structured schema forcing both sides to declare upfront, those gaps tend to surface after a campaign goes live rather than before. The schema makes them detectable at the right moment.

This also reflects a real tension in the market. Publishers are not currently demanding structured data contracts from the platforms building agentic systems on their behalf. Getting the schema right requires someone to do that work proactively, which means it is as much a product decision as a technical one.

## What happened when it ran

Across three rounds, the negotiation produced genuinely commercial behaviour without being prompted for it:

- The seller opened at $10.50 CPM. Rather than negotiating on price, the buyer immediately flagged that "adult content" was missing from the seller's brand safety exclusions. This was a dealbreaker.
- The seller added the exclusion in round 2 without conceding on price, noting it was consistent with their editorial standards anyway.
- The buyer accepted the brand safety fix but countered at $9.75, arguing that the seller's frequency cap of 3 (vs the buyer's preferred 4) creates delivery risk on a 500K impression goal. Fewer ad exposures per person means you need more unique users to hit the same total.
- The seller held at $10.00 in round 3, reframing the tighter cap as a campaign quality benefit rather than a constraint.
- The buyer accepted. Deal reached at $10.00 CPM, $5,000 total spend.
- The system paused and asked for human sign-off before any activation.

Neither agent was told to behave this way. The behaviour came from the constraints in the data contracts and the commercial goals given to each side.

## How it works

Each agent receives a system prompt containing its data contract and a defined set of tools. The tools are the only actions available: make an offer, flag a mismatch, accept a deal, or walk away. The agents cannot do anything outside that set.

The negotiation runs in rounds. Each round, the seller acts first and the buyer responds. The full negotiation history is passed to each agent at the start of their turn so context builds across rounds.

Hard constraints are enforced by the agents themselves. The seller will not go below its floor CPM and the buyer will not exceed its maximum. Softer constraints, like frequency caps and additional conditions, are open to negotiation.

When a deal is reached, the system enters a human review stage. The reviewer sees the full deal terms, a plain English summary, the impression goal, and the estimated total spend. They type approve, reject, or renegotiate. The agents do not proceed until that decision is made.

## How to run it

Add your Anthropic API key to the API_KEY variable at the top of negotiation.py, then run:

```bash
python3 negotiation.py
```

When prompted, type: approve, reject, or renegotiate.

## Stack

- Python 3.9
- Anthropic Claude API (claude-opus-4-6)
- No external libraries beyond the Anthropic SDK

## The human-in-the-loop principle

The agents are autonomous in the middle and constrained at the boundaries. They choose their own negotiating path through the tools, but they cannot activate a campaign. That decision belongs to a human.

This is not a rubber stamp. The reviewer sees the full terms and reasoning before deciding. Someone who knew nothing about the negotiation history could read the sign-off summary and make an informed call.

## Limitations

- Contracts are hardcoded; a production version would pull these from publisher and advertiser databases
- Agents negotiate sequentially rather than simultaneously
- No memory between separate runs
- The negotiation does not yet model campaign flight dates, audience size constraints, or real-time inventory availability