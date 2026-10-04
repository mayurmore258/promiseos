"""PromiseOS ML Dataset Generator.

Generates a realistic, domain-specific labeled dataset for Commitment Classification:
- COMMITMENT vs NON_COMMITMENT
- Core dataset: ~1,000 balanced examples split into Train (70%), Validation (15%), Test (15%).
- Hidden surprise dataset: ~200 separate challenging examples (inputs separated from labels).
- Zero external API dependencies, 100% local, reproducible via fixed random seed.
"""

import csv
import random
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Base paths
ML_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ML_DIR / "datasets"
TRAIN_DIR = DATASETS_DIR / "train"
VAL_DIR = DATASETS_DIR / "validation"
TEST_DIR = DATASETS_DIR / "test"
HIDDEN_DIR = DATASETS_DIR / "hidden"

RANDOM_SEED = 42


def get_commitment_generators():
    """Generators for COMMITMENT examples across various domains, difficulties, and styles."""
    people = ["Rahul", "Priya", "Arjun", "Neha", "Mayur", "Ananya", "Rohan", "Sneha", "Vikram", "Kavya", "David", "Elena", "Alex", "Chen", "Marcus"]
    deliverables = [
        "the financial forecast", "the updated pitch deck", "the quotation spreadsheet",
        "the architecture diagram", "the unit test suite", "the API documentation",
        "the client proposal", "the sprint retrospective notes", "the database migration script",
        "the bug fix patch", "the staging deployment", "the customer refund request",
        "the wireframes for checkout", "the quarterly OKR summary", "the security audit findings",
        "the meeting minutes", "the project timeline", "the revised contract draft",
        "the release candidate build", "the user interview transcripts", "the pricing calculator",
        "the slide deck for tomorrow's demo", "the code review comments", "the invoice breakdown"
    ]
    deadlines = [
        "before 5 PM today", "by end of day tomorrow", "first thing Monday morning",
        "tonight before midnight", "by Friday noon", "by 3 PM this afternoon",
        "before the sprint review tomorrow", "by Wednesday end of day", "within the next two hours",
        "before the client meeting starts", "by tomorrow at 10 AM", "over the weekend"
    ]
    conditions = [
        "If the CI pipeline turns green", "Once the client approves the initial scope",
        "Assuming Arjun finishes reviewing the PR", "If we receive the signed NDA today",
        "As soon as the staging server is back up", "Provided the budget gets cleared by finance",
        "If the designer shares the Figma assets", "Once the security team gives their sign-off"
    ]

    items = []

    # 1. Easy / Direct first-person commitments
    verbs = ["send", "email", "submit", "prepare", "deploy", "finalize", "upload", "deliver", "draft", "share", "write", "compile"]
    for i, d in enumerate(deliverables):
        p = people[i % len(people)]
        dl = deadlines[i % len(deadlines)]
        v = verbs[i % len(verbs)]
        text = f"I'll {v} {d} {dl}."
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": "project" if i % 2 == 0 else "engineering",
            "difficulty": "easy",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": f"Explicit first-person commitment to {v} deliverable with concrete deadline."
        })

        text2 = f"I promise to {v} {d}."
        items.append({
            "text": text2,
            "label": "COMMITMENT",
            "domain": "operations" if i % 2 == 0 else "sales_client",
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": f"Explicit promissory statement committing speaker to {v} {d}."
        })

        text3 = f"I am going to {v} {d} {dl} without fail."
        items.append({
            "text": text3,
            "label": "COMMITMENT",
            "domain": "engineering",
            "difficulty": "easy",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": "Direct undertaking with affirmative emphasis and deadline."
        })

    # 2. Delegated / Assigned third-person commitments
    for i, d in enumerate(deliverables):
        p = people[(i + 3) % len(people)]
        dl = deadlines[(i + 2) % len(deadlines)]
        v = verbs[(i + 1) % len(verbs)]
        text = f"{p} will {v} {d} {dl}."
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": "project",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": f"Delegated commitment assigning ownership of {d} to {p}."
        })

        text_delegated_chat = f"Spoke with {p}; they confirmed they are handling {d} and will send it {dl}."
        items.append({
            "text": text_delegated_chat,
            "label": "COMMITMENT",
            "domain": "operations",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "informal_chat",
            "reason": f"Confirmed delegated undertaking on behalf of {p}."
        })

    # 3. Conditional commitments
    for i, cond in enumerate(conditions):
        d = deliverables[(i + 4) % len(deliverables)]
        dl = deadlines[(i + 1) % len(deadlines)]
        v = verbs[(i + 2) % len(verbs)]
        text = f"{cond}, I will {v} {d} {dl}."
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": "engineering" if i % 2 == 0 else "sales_client",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": True,
            "has_owner": True,
            "language_style": "professional",
            "reason": "Conditional commitment triggered upon condition fulfillment."
        })

        p = people[(i + 5) % len(people)]
        text_cond2 = f"If you can confirm the numbers, {p} and I will {v} {d}."
        items.append({
            "text": text_cond2,
            "label": "COMMITMENT",
            "domain": "executive",
            "difficulty": "hard",
            "has_deadline": False,
            "has_condition": True,
            "has_owner": True,
            "language_style": "formal_email",
            "reason": "Joint conditional commitment tied to user confirmation."
        })

    # 4. Multi-message messy conversations containing commitments
    scenarios = [
        ("Rahul: Did you review the staging logs?\nPriya: Yes, there are several 500 errors in auth.\nRahul: Got it. I'll patch the token validator and push the hotfix tonight.\nPriya: Thanks!",
         "Priya & Rahul", "engineering", "I'll patch the token validator and push the hotfix tonight"),
        ("Mayur: Client wants the quotation before their board meeting.\nArjun: What numbers are we using?\nMayur: Standard enterprise tier. I will calculate the final discount and email them the PDF before 2 PM.\nArjun: Perfect.",
         "Mayur & Arjun", "sales_client", "I will calculate the final discount and email them the PDF before 2 PM"),
        ("Neha: Can someone take care of the catering for Friday?\nVikram: Don't worry, I've got this. I will place the catering order by tomorrow afternoon.\nNeha: Awesome, appreciate it.",
         "Vikram & Neha", "operations", "I will place the catering order by tomorrow afternoon"),
        ("Elena: Hey, did anyone write the lab report for experiment 4?\nAlex: Not yet, everyone is busy with midterms.\nElena: Okay, I'll write the intro and methodology tonight and upload it to the drive.\nAlex: Lifesaver!",
         "Elena & Alex", "academic_student", "I'll write the intro and methodology tonight and upload it to the drive"),
        ("Marcus: We need the board slides revised with Q3 actuals.\nChen: The CFO just sent the updated balance sheet.\nMarcus: Great, I'll update the deck accordingly by 8 AM tomorrow.\nChen: Sounds good.",
         "Marcus & Chen", "executive", "I'll update the deck accordingly by 8 AM tomorrow"),
        ("David: The client is asking about the delay on mobile responsiveness.\nKavya: We found an issue in Safari flexbox.\nDavid: Understood. I will call the client in ten minutes to explain and promise the build by tomorrow.",
         "David & Kavya", "project", "I will call the client in ten minutes to explain and promise the build by tomorrow"),
        ("Ananya: Who is bringing the presentation clicker and adapter?\nSneha: I have them at my desk, I will bring them to conference room B at 11 AM.\nAnanya: Thank you!",
         "Sneha & Ananya", "operations", "I will bring them to conference room B at 11 AM"),
        ("Arjun: Are the integration tests failing on Python 3.11?\nRahul: Yes, some type checking error in auth.\nArjun: Leave it to me. I'll fix the type annotations before our daily standup.\nRahul: Thanks man.",
         "Arjun & Rahul", "engineering", "I'll fix the type annotations before our daily standup"),
    ]
    for text, participants, dom, comm_clause in scenarios:
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "multi_message_messy",
            "reason": f"Messy dialogue containing firm commitment clause: '{comm_clause}'."
        })

    # 5. Informal student / hackathon / team commitments
    informal_commitments = [
        "bro don't stress, I'll finish my part of the slides before midnight.",
        "hey guys, I'm heading out now but I will test the endpoints on my laptop later tonight.",
        "Count on me for the database seeds, will have them ready in 30 mins.",
        "I'll take care of submitting our project on Devpost before the 11:59 PM deadline.",
        "Don't worry about the demo video, I will record the walkthrough and share the Loom link tomorrow morning.",
        "I'll grab the printouts from the library on my way to class.",
        "Yo, I'll ping the TA about the grading rubric by lunch.",
        "I will set up the Supabase instance right after dinner.",
        "Trust me, I'll have the PR ready for review before 9 AM tomorrow.",
        "I got this, will fix the Docker build tonight so we can test tomorrow."
    ]
    for text in informal_commitments:
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": "academic_student",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "informal_chat",
            "reason": "Informal peer dialogue containing clear intent and action commitment."
        })

    # 6. Professional email commitments
    formal_commitments = [
        "Please rest assured that our team will deliver the comprehensive audit report by end of business Thursday.",
        "I am writing to confirm that I will personally oversee the deployment and ensure the hotfix is live by 6 AM tomorrow.",
        "Further to our telephone discussion, I will forward the executed partnership agreement to your office by Monday morning.",
        "We commit to providing a revised statement of work incorporating your requested modifications by 5 PM tomorrow.",
        "I will coordinate with our legal counsel and deliver their feedback regarding clause 7 before Friday noon.",
        "Kindly note that I will compile and transmit the monthly reconciliation report by tomorrow afternoon.",
        "As agreed during the steering committee meeting, I will circulate the updated governance charter prior to our next session.",
        "I will ensure the requested API credentials and documentation are provisioned and sent to your engineering leads by 3 PM."
    ]
    for text in formal_commitments:
        items.append({
            "text": text,
            "label": "COMMITMENT",
            "domain": "executive",
            "difficulty": "easy",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "formal_email",
            "reason": "Formal business commitment with explicit timeline and deliverable."
        })

    # 7. Additional programmatic diverse commitments across domains
    action_templates = [
        ("I will make sure {person} receives the {deliverable} {deadline}.", "project", True, False, "medium"),
        ("Rest assured, I'll investigate {deliverable} and report back {deadline}.", "engineering", True, False, "easy"),
        ("I commit to finalizing {deliverable} as soon as we resolve the open discussion.", "sales_client", False, True, "medium"),
        ("I'll personally verify {deliverable} before we ship the release {deadline}.", "engineering", True, False, "easy"),
        ("We will deliver {deliverable} to your team {deadline}.", "sales_client", True, False, "easy"),
        ("I'm going to take ownership of {deliverable} and deliver it {deadline}.", "project", True, False, "easy"),
        ("I'll handle the paperwork for {deliverable} {deadline}.", "operations", True, False, "easy"),
        ("Count me in for {deliverable}, I will finish it {deadline}.", "academic_student", True, False, "medium"),
        ("I'll send across {deliverable} {deadline}, promise.", "personal_errands", True, False, "easy"),
        ("I will follow up with the vendor regarding {deliverable} {deadline}.", "operations", True, False, "easy"),
        ("If any blocker arises with {deliverable}, I'll notify the channel immediately.", "engineering", False, True, "hard"),
        ("I'll double check the figures for {deliverable} tonight.", "sales_client", True, False, "easy"),
        ("I'll get {person} to sign off on {deliverable} {deadline}.", "executive", True, False, "medium"),
        ("I will upload the latest version of {deliverable} to Google Drive {deadline}.", "project", True, False, "easy"),
        ("I promise I'll look into {deliverable} first thing tomorrow.", "engineering", True, False, "easy"),
        ("I will definitely wrap up {deliverable} {deadline}.", "project", True, False, "easy"),
        ("I am committed to finishing {deliverable} {deadline}.", "project", True, False, "easy"),
        ("You have my word: I'll complete {deliverable} {deadline}.", "sales_client", True, False, "easy"),
        ("I'll take the lead on {deliverable} and have it ready {deadline}.", "operations", True, False, "medium"),
        ("Don't worry, {person} and I will polish {deliverable} {deadline}.", "project", True, False, "medium"),
        ("I'm dedicated to delivering {deliverable} {deadline}.", "engineering", True, False, "easy"),
        ("I will coordinate the sign-off on {deliverable} {deadline}.", "executive", True, False, "medium"),
        ("I'll personally make sure {deliverable} is submitted {deadline}.", "academic_student", True, False, "easy"),
    ]

    for tmpl, dom, has_dl, has_cond, diff in action_templates:
        for idx in range(24):
            p = people[(idx + 1) % len(people)]
            d = deliverables[(idx + 2) % len(deliverables)]
            dl = deadlines[(idx + 3) % len(deadlines)]
            txt = tmpl.format(person=p, deliverable=d, deadline=dl)
            items.append({
                "text": txt,
                "label": "COMMITMENT",
                "domain": dom,
                "difficulty": diff,
                "has_deadline": has_dl,
                "has_condition": has_cond,
                "has_owner": True,
                "language_style": "professional" if dom != "academic_student" else "informal_chat",
                "reason": f"Definite promise/undertaking involving {d}."
            })

    return items


def get_non_commitment_generators():
    """Generators for NON_COMMITMENT examples across various domains, difficulties, and styles."""
    people = ["Rahul", "Priya", "Arjun", "Neha", "Mayur", "Ananya", "Rohan", "Sneha", "Vikram", "Kavya", "David", "Elena", "Alex", "Chen", "Marcus"]
    deliverables = [
        "the financial forecast", "the updated pitch deck", "the quotation spreadsheet",
        "the architecture diagram", "the unit test suite", "the API documentation",
        "the client proposal", "the sprint retrospective notes", "the database migration script",
        "the bug fix patch", "the staging deployment", "the customer refund request",
        "the wireframes for checkout", "the quarterly OKR summary", "the security audit findings",
        "the meeting minutes", "the project timeline", "the revised contract draft",
        "the release candidate build", "the user interview transcripts", "the pricing calculator",
        "the slide deck for tomorrow's demo", "the code review comments", "the invoice breakdown"
    ]
    deadlines = [
        "before 5 PM today", "by end of day tomorrow", "first thing Monday morning",
        "tonight before midnight", "by Friday noon", "by 3 PM this afternoon",
        "before the sprint review tomorrow", "by Wednesday end of day", "within the next two hours",
        "before the client meeting starts", "by tomorrow at 10 AM", "over the weekend"
    ]

    items = []

    # 1. Questions & Inquiries (NON_COMMITMENT)
    for i, d in enumerate(deliverables):
        p = people[i % len(people)]
        dl = deadlines[i % len(deadlines)]
        text_q1 = f"Can you send {d} {dl}?"
        items.append({
            "text": text_q1,
            "label": "NON_COMMITMENT",
            "domain": "project",
            "difficulty": "easy",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Request/question asking recipient; speaker does not make a commitment."
        })

        text_q2 = f"Who is responsible for preparing {d}?"
        items.append({
            "text": text_q2,
            "label": "NON_COMMITMENT",
            "domain": "operations",
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Informational inquiry regarding responsibility."
        })

        text_q3 = f"Did {p} already finish {d}?"
        items.append({
            "text": text_q3,
            "label": "NON_COMMITMENT",
            "domain": "project",
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Status question about past action."
        })

    # 2. Requests & Instructions directed at others (NON_COMMITMENT)
    for i, d in enumerate(deliverables):
        p = people[(i + 2) % len(people)]
        dl = deadlines[(i + 1) % len(deadlines)]
        text_req1 = f"Please send me {d} {dl} if possible."
        items.append({
            "text": text_req1,
            "label": "NON_COMMITMENT",
            "domain": "sales_client",
            "difficulty": "easy",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Imperative request to another party without mutual commitment."
        })

        text_req2 = f"{p}, kindly make sure {d} is uploaded {dl}."
        items.append({
            "text": text_req2,
            "label": "NON_COMMITMENT",
            "domain": "operations",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": False,
            "language_style": "formal_email",
            "reason": "Directive instructing someone else to perform a task."
        })

    # 3. Opinions, Suggestions & Speculation (NON_COMMITMENT)
    for i, d in enumerate(deliverables):
        dl = deadlines[(i + 3) % len(deadlines)]
        text_op1 = f"We should probably finalize {d} {dl}."
        items.append({
            "text": text_op1,
            "label": "NON_COMMITMENT",
            "domain": "project",
            "difficulty": "medium",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Advisory suggestion / opinion ('should probably') without personal undertaking."
        })

        text_op2 = f"In my opinion, {d} needs a complete redesign."
        items.append({
            "text": text_op2,
            "label": "NON_COMMITMENT",
            "domain": "engineering",
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": "Subjective opinion regarding quality."
        })

    # 4. Weak intentions & Ambiguous thoughts without commitment (NON_COMMITMENT - Policy)
    for i, d in enumerate(deliverables):
        dl = deadlines[(i + 4) % len(deadlines)]
        text_int1 = f"I'm thinking about working on {d} {dl}."
        items.append({
            "text": text_int1,
            "label": "NON_COMMITMENT",
            "domain": "project",
            "difficulty": "hard",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "informal_chat",
            "reason": "Weak intention ('thinking about') lacks promissory undertaking."
        })

        text_int2 = f"I might check {d} if I get some free time."
        items.append({
            "text": text_int2,
            "label": "NON_COMMITMENT",
            "domain": "engineering",
            "difficulty": "hard",
            "has_deadline": False,
            "has_condition": True,
            "has_owner": True,
            "language_style": "informal_chat",
            "reason": "Tentative possibility ('might') conditional on free time, not a binding commitment."
        })

        text_int3 = f"I hope to finish {d} soon."
        items.append({
            "text": text_int3,
            "label": "NON_COMMITMENT",
            "domain": "operations",
            "difficulty": "hard",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": "Aspirational statement ('hope to') without commitment guarantee."
        })

    # 5. Factual statements & Status reports (NON_COMMITMENT)
    facts = [
        ("The production server CPU utilization spiked to 98% at 3 AM.", "engineering", "Status event report"),
        ("We received 45 customer inquiries regarding the new pricing tiers.", "sales_client", "Factual metrics summary"),
        ("The quarterly review meeting has been scheduled for Thursday at 2 PM.", "operations", "Calendar notification"),
        ("The build artifact is 142 MB and passed all unit test fixtures.", "engineering", "Build telemetry statement"),
        ("The office will remain closed next Monday for the national holiday.", "operations", "General administrative announcement"),
        ("Last week's revenue exceeded the initial target by roughly twelve percent.", "executive", "Historical financial performance statement"),
        ("The API returned a 404 error when querying the user profiles endpoint.", "engineering", "Technical incident observation"),
        ("Rahul and Priya attended the design review yesterday afternoon.", "project", "Past event summary"),
        ("Our current sprint contains 34 story points with 5 days remaining.", "project", "Sprint status fact"),
        ("The contract includes a standard 30-day cancellation clause.", "sales_client", "Contractual statement of fact"),
    ]
    for text, dom, reason in facts:
        items.append({
            "text": text,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "professional",
            "reason": reason
        })

    # 6. Conversational noise, pleasantries, banter (NON_COMMITMENT)
    pleasantries = [
        ("Thanks for the update, really appreciate the quick turnaround!", "project", "Pleasantry / gratitude"),
        ("Haha that meme you posted in general chat was hilarious.", "academic_student", "Informal social banter"),
        ("Great job on the demo presentation today everyone, loved the slides.", "executive", "Praise / acknowledgment"),
        ("Good morning team, let me know if anyone wants to grab coffee.", "operations", "Social greeting"),
        ("Sounds good to me, see you all in the meeting room in five minutes.", "project", "Meeting transition acknowledgment"),
        ("Understood, I will let you know if we have any further questions.", "sales_client", "Standard closing pleasantry"),
        ("Happy Friday everyone, have a wonderful weekend!", "operations", "Weekend greeting"),
        ("Awesome, thanks! 👍", "academic_student", "Brief conversational confirmation"),
        ("No worries at all, take your time.", "personal_errands", "Casual acknowledgment"),
        ("Let me read through this thread and catch up with what happened.", "project", "Orientation note without deliverable undertaking"),
    ]
    for text, dom, reason in pleasantries:
        items.append({
            "text": text,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "easy",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "informal_chat",
            "reason": reason
        })

    # 7. Explicit Negations (NON_COMMITMENT)
    negations = [
        "I will not be able to attend the project sync tomorrow morning.",
        "I cannot promise that the feature will be ready before the sprint ends.",
        "I won't have time to review your pull request tonight.",
        "We are definitely not going to support legacy Internet Explorer browsers.",
        "I can't commit to delivering the revised quotation by 5 PM today.",
        "Sorry, I am unable to take on any additional tasks this week.",
        "I won't be handling the customer negotiations for this account.",
        "Our team will not deploy any changes during the holiday freeze period.",
    ]
    for text in negations:
        items.append({
            "text": text,
            "label": "NON_COMMITMENT",
            "domain": "project",
            "difficulty": "hard",
            "has_deadline": True,
            "has_condition": False,
            "has_owner": True,
            "language_style": "professional",
            "reason": "Explicit refusal / non-commitment statement stating inability to commit."
        })

    # 8. Messy conversations WITHOUT commitments (NON_COMMITMENT)
    messy_non_commitments = [
        ("Rahul: Did you see the updated Figma links?\nPriya: Yes, looking at them now.\nRahul: The mobile layout looks a bit cramped.\nPriya: Agreed, let's bring it up in tomorrow's design critique.",
         "Rahul & Priya", "project", "Discussion evaluating design without actionable promise"),
        ("Mayur: How was the client call today?\nArjun: Pretty intense, they asked about SOC2 compliance.\nMayur: Do we have the documentation ready?\nArjun: Sarah might know more about that.",
         "Mayur & Arjun", "sales_client", "Informational recap without commitment"),
        ("Neha: Is the conference room free at 4 PM?\nVikram: I think the marketing team booked it until 5.\nNeha: Alright, we can just do a Google Meet instead.\nVikram: Works for me.",
         "Vikram & Neha", "operations", "Logistical room check with no promise"),
        ("Elena: Did everyone understand problem 3 on the problem set?\nAlex: No, the second part was super tricky.\nElena: Yeah, the professor said the hint is in chapter 4.\nAlex: I should read that chapter.",
         "Elena & Alex", "academic_student", "Study discussion with speculative reflection ('I should read')"),
        ("Marcus: What is the current runway estimate from the audit?\nChen: Roughly 14 months at current burn rate.\nMarcus: That gives us enough time for the Series B.\nChen: Exactly.",
         "Marcus & Chen", "executive", "Financial status conversation without action undertaking"),
        ("David: Has anyone seen my blue notebook?\nKavya: Check near the coffee machine on the 3rd floor.\nDavid: Ah thanks, found it!\nKavya: Nice!",
         "David & Kavya", "personal_errands", "Casual lost item search"),
    ]
    for text, participants, dom, reason in messy_non_commitments:
        items.append({
            "text": text,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": False,
            "has_condition": False,
            "has_owner": False,
            "language_style": "multi_message_messy",
            "reason": f"Messy dialogue containing {reason}."
        })

    # 9. Additional programmatic non-commitments
    non_comm_templates = [
        ("Could you please review {deliverable} when you have a moment?", "engineering", True, False, "easy"),
        ("Is {deliverable} expected to be completed {deadline}?", "project", True, False, "easy"),
        ("I think {deliverable} was already approved by {person}.", "operations", False, False, "medium"),
        ("We might want to revisit {deliverable} next quarter.", "executive", False, False, "medium"),
        ("Why was {deliverable} not updated in the shared folder?", "operations", False, False, "easy"),
        ("Can we discuss {deliverable} during our 1-on-1 meeting?", "project", False, False, "easy"),
        ("I wonder if {person} has looked at {deliverable} yet.", "project", False, False, "medium"),
        ("Please ensure that {deliverable} follows the new formatting guidelines.", "sales_client", False, False, "easy"),
        ("It would be great if someone could take a look at {deliverable}.", "engineering", False, False, "hard"),
        ("I'm not sure if {deliverable} is ready for client review.", "sales_client", False, False, "medium"),
        ("Does anyone have feedback on {deliverable}?", "academic_student", False, False, "easy"),
        ("Maybe {person} can help us with {deliverable}.", "project", False, False, "hard"),
        ("Have you had a chance to inspect {deliverable}?", "engineering", False, False, "easy"),
        ("The deadline for {deliverable} has been pushed to next week.", "project", True, False, "medium"),
        ("I wish we had more time to work on {deliverable}.", "academic_student", False, False, "hard"),
        ("I was wondering if {deliverable} is ready yet.", "project", False, False, "easy"),
        ("Can someone remind me who was working on {deliverable}?", "operations", False, False, "easy"),
        ("I heard rumors that {deliverable} might get cancelled.", "executive", False, False, "medium"),
        ("Is there any update on {deliverable} {deadline}?", "project", True, False, "easy"),
        ("We discussed {deliverable} during yesterday's standup.", "engineering", False, False, "easy"),
        ("I sent the completed version of {deliverable} yesterday.", "project", False, False, "hard"),
        ("{person} already submitted {deliverable} this morning.", "operations", False, False, "hard"),
        ("We should wait before making any decisions about {deliverable}.", "executive", False, False, "medium"),
    ]

    for tmpl, dom, has_dl, has_cond, diff in non_comm_templates:
        for idx in range(24):
            p = people[(idx + 2) % len(people)]
            d = deliverables[(idx + 3) % len(deliverables)]
            dl = deadlines[(idx + 4) % len(deadlines)]
            txt = tmpl.format(person=p, deliverable=d, deadline=dl)
            items.append({
                "text": txt,
                "label": "NON_COMMITMENT",
                "domain": dom,
                "difficulty": diff,
                "has_deadline": has_dl,
                "has_condition": has_cond,
                "has_owner": False,
                "language_style": "professional" if dom != "academic_student" else "informal_chat",
                "reason": f"Non-commitment statement regarding {d}."
            })

    return items


def generate_hidden_surprise_examples() -> Tuple[List[Dict], List[Dict]]:
    """Generates 200 distinct, challenging hidden evaluation examples.
    
    Includes tricky edge cases, paraphrases, adversarial distractors, and indirect commitments.
    Returns (inputs_list, labels_list).
    """
    hidden_raw = [
        # Tricky Commitments
        ("I'll have the updated pricing matrix in your inbox before lunch, guaranteed.", "COMMITMENT", "sales_client", "hard", True, False, "Explicit promissory guarantee with deadline"),
        ("Assuming the API key arrives, I'll integrate the payment gateway tonight.", "COMMITMENT", "engineering", "hard", True, True, "Conditional undertaking with concrete trigger"),
        ("Don't worry about the presentation clicker, I will bring my spare one to the room at 9 AM.", "COMMITMENT", "operations", "medium", True, False, "Reassurance coupled with concrete physical deliverable commitment"),
        ("Mayur confirmed he will push the database migration before 11 PM.", "COMMITMENT", "engineering", "medium", True, False, "Third-person verified commitment"),
        ("I will draft the response to the customer complaint right after this standup.", "COMMITMENT", "sales_client", "easy", True, False, "First-person commitment tied to event deadline"),
        ("Team: I'm taking full responsibility for the broken build; fixing it now and deploying by 2 AM.", "COMMITMENT", "engineering", "hard", True, False, "Accountability acceptance with deployment undertaking"),
        ("I'll send you the Figma prototype as soon as I finish the responsive breakpoint.", "COMMITMENT", "project", "medium", False, True, "Conditional artifact delivery commitment"),
        ("I promise to review all 14 student applications before the committee meets on Tuesday.", "COMMITMENT", "academic_student", "easy", True, False, "Promissory commitment with explicit count and date"),
        ("Leave the invoice dispute to me; I will call their accounting department tomorrow morning.", "COMMITMENT", "operations", "medium", True, False, "Delegated responsibility acceptance with time window"),
        ("I will compile the executive summary and email it to the board prior to Friday's call.", "COMMITMENT", "executive", "easy", True, False, "Formal executive deliverable commitment"),
        
        # Tricky Non-Commitments
        ("I really should send the revised quotation to the client soon.", "NON_COMMITMENT", "sales_client", "hard", False, False, "Modal obligation ('should') without actual commitment"),
        ("Can we make sure someone checks the backup logs before Friday?", "NON_COMMITMENT", "engineering", "hard", True, False, "Group question/suggestion without individual undertaking"),
        ("I was hoping to finish the slide deck tonight, but I feel under the weather.", "NON_COMMITMENT", "project", "hard", True, False, "Unrealized intention aborted due to illness"),
        ("Please remember to turn off the lab equipment when you leave tonight.", "NON_COMMITMENT", "academic_student", "medium", True, False, "Reminder instruction directed at others"),
        ("In my view, we must prioritize user privacy over speed.", "NON_COMMITMENT", "engineering", "easy", False, False, "Value judgment / ethical stance"),
        ("I won't be able to prepare the quarterly balance sheet this month.", "NON_COMMITMENT", "executive", "hard", True, False, "Explicit refusal / negative commitment"),
        ("Did you see the client's email regarding the price negotiation?", "NON_COMMITMENT", "sales_client", "easy", False, False, "Status query about incoming communication"),
        ("Great job on finishing the sprint goals ahead of schedule!", "NON_COMMITMENT", "project", "easy", False, False, "Recognition / celebration note"),
        ("I might take a look at the pull request if time permits tomorrow.", "NON_COMMITMENT", "engineering", "hard", True, True, "Weak hypothetical possibility ('might') without obligation"),
        ("The system outage lasted for approximately forty-three minutes yesterday.", "NON_COMMITMENT", "operations", "easy", False, False, "Historical incident reporting fact"),
    ]

    # Expand systematically to reach 200 high-quality unique surprise examples
    adversarial_templates = [
        # Commitment templates
        ("Rest assured that I will finalize {item} {time}.", "COMMITMENT", "project", "hard", True, False, "Assurance with affirmative future commitment"),
        ("I'm locking myself in to finish {item} {time}.", "COMMITMENT", "engineering", "hard", True, False, "Colloquial intense personal commitment"),
        ("If {person} provides the logs, I will diagnose the issue {time}.", "COMMITMENT", "engineering", "hard", True, True, "Conditional technical undertaking"),
        ("I will personally deliver {item} to the department office {time}.", "COMMITMENT", "academic_student", "medium", True, False, "Personal delivery commitment"),
        ("Count on me: {item} will be completed and uploaded {time}.", "COMMITMENT", "operations", "medium", True, False, "Explicit promissory undertaking"),
        # Non-commitment templates
        ("Do you think we should submit {item} {time}?", "NON_COMMITMENT", "academic_student", "hard", True, False, "Question consulting others on timing"),
        ("I am considering rewriting {item} whenever we get a chance.", "NON_COMMITMENT", "engineering", "hard", False, False, "Vague speculative consideration"),
        ("It would be wonderful if {item} could be ready {time}.", "NON_COMMITMENT", "executive", "hard", True, False, "Wishful thinking / aspiration"),
        ("I definitely cannot commit to {item} {time}.", "NON_COMMITMENT", "project", "hard", True, False, "Direct explicit refusal to commit"),
        ("Was {item} sent to the client {time}?", "NON_COMMITMENT", "sales_client", "easy", True, False, "Inquiry about past deliverable status"),
    ]

    surprise_items = [
        "the disaster recovery plan", "the security checklist", "the quarterly tax filing",
        "the localization assets", "the onboarding walkthrough", "the sprint burndown chart",
        "the vendor contract appendix", "the performance benchmark report", "the compliance questionnaire",
        "the accessibility audit review"
    ]
    surprise_times = [
        "by 4 PM today", "before the close of business tomorrow", "first thing Monday",
        "prior to the release window", "by tomorrow noon", "before midnight tonight"
    ]
    surprise_people = ["Priya", "Rahul", "Mayur", "Alex", "David", "Elena", "Vikram", "Sneha"]

    counter = 0
    all_hidden = list(hidden_raw)

    for tmpl, label, dom, diff, has_dl, has_cond, rsn in adversarial_templates:
        for idx in range(18):
            it = surprise_items[(idx + counter) % len(surprise_items)]
            tm = surprise_times[(idx + counter) % len(surprise_times)]
            pp = surprise_people[(idx + counter) % len(surprise_people)]
            txt = tmpl.format(item=it, time=tm, person=pp)
            all_hidden.append((txt, label, dom, diff, has_dl, has_cond, rsn))
            counter += 1

    # Ensure exactly 200 items, perfectly balanced (100 COMMITMENT, 100 NON_COMMITMENT)
    comms = [h for h in all_hidden if h[1] == "COMMITMENT"][:100]
    non_comms = [h for h in all_hidden if h[1] == "NON_COMMITMENT"][:100]

    balanced_hidden = comms + non_comms
    random.Random(RANDOM_SEED + 999).shuffle(balanced_hidden)

    inputs = []
    labels = []

    for i, item in enumerate(balanced_hidden):
        hid_id = f"hidden_{i+1:04d}"
        txt, lbl, dom, diff, has_dl, has_cond, rsn = item
        inputs.append({
            "id": hid_id,
            "text": txt,
            "domain": dom,
            "difficulty": diff,
            "has_deadline": has_dl,
            "has_condition": has_cond,
            "has_owner": True if lbl == "COMMITMENT" else False,
            "language_style": "professional" if dom != "academic_student" else "informal_chat",
            "source_type": "synthetic_adversarial"
        })
        labels.append({
            "id": hid_id,
            "label": lbl,
            "reason": rsn
        })

    return inputs, labels


def generate_all_datasets():
    """Generates the full suite of datasets: Train, Validation, Test, and Hidden."""
    print("Generating PromiseOS Commitment Classification datasets...")
    random.seed(RANDOM_SEED)

    commitments = get_commitment_generators()
    non_commitments = get_non_commitment_generators()

    # Deduplicate within pools
    def dedupe(pool: List[Dict]) -> List[Dict]:
        seen = set()
        unique = []
        for x in pool:
            norm = x["text"].strip().lower()
            if norm not in seen:
                seen.add(norm)
                unique.append(x)
        return unique

    commitments = dedupe(commitments)
    non_commitments = dedupe(non_commitments)

    print(f"Unique commitment candidates: {len(commitments)}")
    print(f"Unique non-commitment candidates: {len(non_commitments)}")

    # We want ~1000 total core examples: 500 commitments, 500 non-commitments
    target_each = min(len(commitments), len(non_commitments), 500)
    commitments = commitments[:target_each]
    non_commitments = non_commitments[:target_each]

    # Stratified shuffle into splits: 70% Train, 15% Validation, 15% Test
    rng = random.Random(RANDOM_SEED)
    rng.shuffle(commitments)
    rng.shuffle(non_commitments)

    train_c_count = int(target_each * 0.70)
    val_c_count = int(target_each * 0.15)
    test_c_count = target_each - train_c_count - val_c_count

    train_items = commitments[:train_c_count] + non_commitments[:train_c_count]
    val_items = commitments[train_c_count:train_c_count + val_c_count] + non_commitments[train_c_count:train_c_count + val_c_count]
    test_items = commitments[train_c_count + val_c_count:] + non_commitments[train_c_count + val_c_count:]

    rng.shuffle(train_items)
    rng.shuffle(val_items)
    rng.shuffle(test_items)

    # Assign IDs
    for i, it in enumerate(train_items):
        it["id"] = f"train_{i+1:04d}"
        it["source_type"] = "synthetic_curated"

    for i, it in enumerate(val_items):
        it["id"] = f"val_{i+1:04d}"
        it["source_type"] = "synthetic_curated"

    for i, it in enumerate(test_items):
        it["id"] = f"test_{i+1:04d}"
        it["source_type"] = "synthetic_curated"

    # Write Train, Val, Test CSVs
    fieldnames = ["id", "text", "label", "domain", "difficulty", "has_deadline", "has_condition", "has_owner", "language_style", "source_type", "reason"]

    def write_csv(path: Path, items: List[Dict]):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for it in items:
                writer.writerow(it)

    write_csv(TRAIN_DIR / "train.csv", train_items)
    write_csv(VAL_DIR / "validation.csv", val_items)
    write_csv(TEST_DIR / "test.csv", test_items)

    # Generate Hidden Dataset (200 balanced, tricky samples)
    hidden_inputs, hidden_labels = generate_hidden_surprise_examples()

    # Check for leakage between train/val/test and hidden
    core_texts = {x["text"].strip().lower() for x in (train_items + val_items + test_items)}
    hidden_texts = {x["text"].strip().lower() for x in hidden_inputs}
    leakage = core_texts.intersection(hidden_texts)
    if leakage:
        raise ValueError(f"Leakage detected between core datasets and hidden surprise set: {len(leakage)} overlapping samples!")

    # Write Hidden Inputs
    HIDDEN_DIR.mkdir(parents=True, exist_ok=True)
    hidden_input_fields = ["id", "text", "domain", "difficulty", "has_deadline", "has_condition", "has_owner", "language_style", "source_type"]
    with open(HIDDEN_DIR / "hidden_inputs.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=hidden_input_fields)
        writer.writeheader()
        for it in hidden_inputs:
            writer.writerow(it)

    # Write Hidden Labels
    hidden_label_fields = ["id", "label", "reason"]
    with open(HIDDEN_DIR / "hidden_labels.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=hidden_label_fields)
        writer.writeheader()
        for it in hidden_labels:
            writer.writerow(it)

    print("\nDataset Generation Complete:")
    print(f"  Train:      {len(train_items)} ({sum(1 for x in train_items if x['label'] == 'COMMITMENT')} C / {sum(1 for x in train_items if x['label'] == 'NON_COMMITMENT')} NC)")
    print(f"  Validation: {len(val_items)} ({sum(1 for x in val_items if x['label'] == 'COMMITMENT')} C / {sum(1 for x in val_items if x['label'] == 'NON_COMMITMENT')} NC)")
    print(f"  Test:       {len(test_items)} ({sum(1 for x in test_items if x['label'] == 'COMMITMENT')} C / {sum(1 for x in test_items if x['label'] == 'NON_COMMITMENT')} NC)")
    print(f"  Hidden:     {len(hidden_inputs)} ({sum(1 for x in hidden_labels if x['label'] == 'COMMITMENT')} C / {sum(1 for x in hidden_labels if x['label'] == 'NON_COMMITMENT')} NC)")
    print(f"  Total:      {len(train_items) + len(val_items) + len(test_items) + len(hidden_inputs)} examples")
    print(f"  Zero Leakage Verified: {len(leakage)} overlaps found.")


if __name__ == "__main__":
    generate_all_datasets()
