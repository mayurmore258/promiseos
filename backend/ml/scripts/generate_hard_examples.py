"""Targeted Hard Examples Generator for PromiseOS ML Model Improvement Round 2.

Generates 440 high-difficulty, original examples covering:
- NON_COMMITMENT: Questions with deliverables/deadlines, speculative/hesitant phrasing,
  adversarial negations, requests/imperatives, third-party reporting, habitual/factual statements,
  and counterfactual hypotheticals.
- COMMITMENT: Direct strong undertakings, colloquial/idiomatic commitments ("count on me",
  "i'm on it", "consider it done"), multi-sentence conversational undertakings, conditional
  undertakings, team commitments, academic/student deadlines, and executive/SLA commitments.

Outputs:
- backend/ml/datasets/hard_augmentation/hard_examples.csv (440 total)
- backend/ml/datasets/hard_augmentation/hard_train.csv (320 items: 160 C, 160 NC)
- backend/ml/datasets/hard_augmentation/hard_validation.csv (120 items: 60 C, 60 NC)

Strictly zero overlap with existing core splits or hidden dataset.
"""

import csv
import random
from pathlib import Path
from typing import Dict, List, Set
import pandas as pd

ML_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = ML_DIR / "datasets"
AUG_DIR = DATASETS_DIR / "hard_augmentation"

RANDOM_SEED = 42


def build_hard_non_commitments() -> List[Dict]:
    """Builds 220 difficult NON_COMMITMENT examples."""
    items = []

    # Category A: Questions containing deliverables, action verbs, or deadlines (50 examples)
    questions = [
        ("Will you be able to push the hotfix before tonight's deployment?", "engineering", "chat", True, False, True),
        ("Are you planning to email the revised invoice to the client before Friday?", "sales_client", "email", True, False, True),
        ("Can someone from your squad submit the security audit responses by 3 PM?", "engineering", "slack", True, False, False),
        ("Did you already finish updating the database migration scripts?", "engineering", "chat", False, False, True),
        ("Could you check if the API documentation was delivered on time?", "project", "ticket", False, False, True),
        ("Would it be possible for you to share the deck before our 10 AM sync?", "executive", "email", True, False, True),
        ("Has anyone started drafting the customer refund policy yet?", "operations", "slack", False, False, False),
        ("Why haven't we received the sprint metrics report from the data team?", "project", "meeting_transcript", False, False, False),
        ("Who is responsible for deploying the release candidate by midnight?", "engineering", "slack", True, False, False),
        ("When do you think the client presentation will be ready?", "sales_client", "chat", False, False, True),
        ("Do you think Priya can finish the wireframes before Monday morning?", "project", "slack", True, False, True),
        ("Are we still expecting Alex to upload the financial forecast today?", "operations", "meeting_transcript", True, False, True),
        ("Could someone take a look at the checkout service error logs?", "engineering", "ticket", False, False, False),
        ("Is Mayur going to send the quarterly OKR summary this afternoon?", "executive", "email", True, False, True),
        ("Should we prepare the pitch deck before meeting the investors tomorrow?", "executive", "chat", True, False, False),
        ("Did Rahul mention when he will deliver the quotation spreadsheet?", "sales_client", "slack", False, False, True),
        ("Can you find out if the client signed the NDA?", "sales_client", "email", False, False, True),
        ("Will the staging cluster be restored before the sprint demo at 4 PM?", "engineering", "slack", True, False, False),
        ("Have you reviewed the pull request that Arjun opened yesterday?", "engineering", "chat", False, False, True),
        ("Could you remind Sneha to compile the meeting minutes?", "operations", "slack", False, False, True),
        ("Are you free to help write the unit test suite over the weekend?", "academic_student", "chat", True, False, True),
        ("Do you know who will handle the customer escalations tonight?", "operations", "slack", True, False, False),
        ("Can we schedule the architecture review for Wednesday noon?", "engineering", "email", True, False, False),
        ("Did Elena confirm whether she will submit the lab report before midnight?", "academic_student", "chat", True, False, True),
        ("Would you mind looking over my resume draft before Friday?", "personal_errands", "chat", True, False, True),
        ("Will there be enough time to finalize the release notes tomorrow morning?", "project", "meeting_transcript", True, False, False),
        ("Is it feasible to deliver the pricing calculator within the next two weeks?", "sales_client", "email", True, False, False),
        ("Can someone verify the bug fix patch on the test environment?", "engineering", "ticket", False, False, False),
        ("Have we decided who is presenting the project timeline to stakeholders?", "project", "meeting_transcript", False, False, False),
        ("Could you let me know when the revised contract draft is ready?", "sales_client", "chat", False, False, True),
        ("Did the QA team finish running the regression tests for the build?", "engineering", "slack", False, False, True),
        ("Will you send me the tracking link when the package arrives?", "personal_errands", "chat", False, True, True),
        ("Are we required to submit the capstone proposal by 5 PM today?", "academic_student", "slack", True, False, False),
        ("Who should I contact regarding the user interview transcripts?", "project", "ticket", False, False, False),
        ("Can you check with finance whether the vendor payment cleared?", "operations", "slack", False, False, True),
        ("Is there any update on the security vulnerability remediation ticket?", "engineering", "ticket", False, False, False),
        ("Should I wait for your approval before emailing the client?", "sales_client", "email", False, True, True),
        ("Did you manage to review the revised slide deck for tomorrow's demo?", "executive", "chat", True, False, True),
        ("Will anyone be available to monitor the release overnight?", "engineering", "slack", True, False, False),
        ("Can we get an extension on the project deliverable deadline?", "academic_student", "email", False, False, False),
        ("Do you want me to forward the code review comments to David?", "engineering", "slack", False, False, True),
        ("Has the client accepted the proposed milestone dates?", "sales_client", "meeting_transcript", False, False, False),
        ("Could you please confirm receipt of the invoice breakdown?", "operations", "email", False, False, True),
        ("Are you planning on fixing the broken CSS layout before Friday?", "engineering", "chat", True, False, True),
        ("Why was the database backup script disabled during the maintenance window?", "engineering", "ticket", False, False, False),
        ("Did you see the feedback Neha posted on the wireframes?", "project", "slack", False, False, True),
        ("Will you be in the office tomorrow to hand over the hardware tokens?", "operations", "chat", True, False, True),
        ("Can we review the sprint burndown chart together after lunch?", "project", "meeting_transcript", False, False, False),
        ("Is someone going to update the production deployment runbook?", "engineering", "slack", False, False, False),
        ("Could you please send over the WiFi credentials for the guest room?", "personal_errands", "chat", False, False, True),
    ]
    for q, dom, src, dl, cond, owner in questions:
        items.append({
            "text": q,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Interrogative utterance asking a question, not an affirmative undertaking by the speaker."
        })

    # Category B: Speculation / Hesitation / Tentative Language (40 examples)
    speculations = [
        ("I might try to look over the financial forecast tomorrow if my schedule clears up.", "operations", "chat", True, True, True),
        ("I think I'll probably get around to reviewing the PR sometime next week.", "engineering", "slack", True, False, True),
        ("I may be able to draft a rough outline by Friday, but don't count on it.", "project", "slack", True, False, True),
        ("There's a slight chance I can attend the demo and provide feedback tonight.", "engineering", "chat", True, False, True),
        ("Perhaps we can discuss the contract revisions later this week.", "sales_client", "email", False, False, False),
        ("I'm hoping to finish the slide deck before Monday, though I have back-to-back meetings.", "executive", "email", True, False, True),
        ("It's possible I could take a quick look at the bug report over the weekend.", "engineering", "chat", True, False, True),
        ("I'll consider helping with the migration if nothing else catches fire.", "engineering", "slack", False, True, True),
        ("We might send a preliminary version if we manage to finish early.", "project", "slack", False, True, False),
        ("I might be free to check the test results tomorrow afternoon.", "academic_student", "chat", True, False, True),
        ("Maybe I can write some documentation once the main feature is tested.", "engineering", "slack", False, True, True),
        ("I could potentially help you with the grocery run later today.", "personal_errands", "chat", True, False, True),
        ("I'm leaning towards reviewing the candidates on Thursday if time permits.", "operations", "email", True, True, True),
        ("There is some probability that we will update the pricing sheet soon.", "sales_client", "email", False, False, False),
        ("I think the team might deploy the patch sometime before Friday.", "engineering", "meeting_transcript", True, False, False),
        ("It is conceivable that I could deliver a rough sketch before the meeting.", "project", "chat", False, False, True),
        ("I may look at the API endpoints later tonight if I don't get too tired.", "engineering", "chat", True, True, True),
        ("We could perhaps schedule a follow-up call next Tuesday.", "sales_client", "email", True, False, False),
        ("I might be able to clean up the repository branches over the weekend.", "engineering", "slack", True, False, True),
        ("I think I could possibly draft the release announcement tomorrow.", "project", "chat", True, False, True),
        ("Maybe Sneha will send the spreadsheet, but she wasn't certain.", "operations", "slack", False, False, True),
        ("I may drop by the lab to run the benchmark script if the server is available.", "academic_student", "chat", False, True, True),
        ("I'll try my best to see if I can finish the slide design by noon.", "executive", "chat", True, False, True),
        ("We might consider revisiting the database indexing strategy next quarter.", "engineering", "meeting_transcript", False, False, False),
        ("I could possibly prepare a summary if the manager explicitly asks for it.", "operations", "chat", False, True, True),
        ("Perhaps I can join the customer troubleshooting session for 10 minutes.", "sales_client", "slack", False, False, True),
        ("I might get a chance to inspect the crash logs before heading out.", "engineering", "chat", False, False, True),
        ("It's up in the air whether I'll be able to send the proposal tomorrow.", "sales_client", "slack", True, False, True),
        ("I am thinking about reviewing the architecture document later tonight.", "engineering", "chat", True, False, True),
        ("We may or may not push the update depending on QA feedback.", "engineering", "slack", False, True, False),
        ("I'll see if I have bandwidth to help with the invoice breakdown tomorrow.", "operations", "chat", True, False, True),
        ("Maybe we can wrap up the user research synthesis before next sprint.", "project", "slack", False, False, False),
        ("I might have an hour to dedicate to the thesis bibliography tonight.", "academic_student", "chat", True, False, True),
        ("There is a chance I'll stop by the bank before 4 PM today.", "personal_errands", "chat", True, False, True),
        ("I could conceivably finish the script before the deadline if uninterrupted.", "engineering", "slack", False, True, True),
        ("I'm doubtful I can deliver the presentation by tomorrow, but I might try.", "executive", "email", True, False, True),
        ("We might send an update if anything changes with the client.", "sales_client", "chat", False, True, False),
        ("I may be available to glance over the test plan during lunch.", "engineering", "slack", False, False, True),
        ("I think I can probably send the receipt once I find where it saved.", "personal_errands", "chat", False, True, True),
        ("It's possible we will look into adding that feature in a future sprint.", "project", "ticket", False, False, False),
    ]
    for s, dom, src, dl, cond, owner in speculations:
        items.append({
            "text": s,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Speculative or tentative statement lacking definitive commitment to act."
        })

    # Category C: Adversarial Negation, Explicit Refusal, and Negative Declarations (40 examples)
    negations = [
        ("I won't send the financial forecast today because the underlying ledger hasn't balanced.", "operations", "slack", True, True, True),
        ("I am definitely not going to deploy this service without peer review.", "engineering", "slack", False, True, True),
        ("I never promised to finish the frontend integration by Wednesday.", "engineering", "meeting_transcript", True, False, True),
        ("I cannot commit to delivering the pitch deck before Monday morning.", "executive", "email", True, False, True),
        ("We will not be submitting the vendor RFP response this quarter.", "sales_client", "email", False, False, False),
        ("I refuse to sign off on the production deployment until load testing passes.", "engineering", "ticket", False, True, True),
        ("No way am I taking ownership of the customer refund backlog.", "operations", "chat", False, False, True),
        ("I am not going to write the unit tests for their legacy service.", "engineering", "slack", False, False, True),
        ("Under no circumstances will I approve this pull request before the linter passes.", "engineering", "ticket", False, True, True),
        ("I won't be preparing the sprint retrospective slides for this iteration.", "project", "chat", False, False, True),
        ("I cannot guarantee that the bug will be resolved before the release.", "engineering", "slack", False, False, True),
        ("I'm not sending any emails to the client until management confirms our position.", "sales_client", "slack", False, True, True),
        ("We are not committing to any deadlines until the requirements are locked down.", "project", "meeting_transcript", False, True, False),
        ("I didn't agree to handle the database migration by myself.", "engineering", "chat", False, False, True),
        ("I won't take on additional tickets while our current sprint is overloaded.", "engineering", "ticket", False, False, True),
        ("There is no way I can deliver the revised quotation before 2 PM today.", "sales_client", "email", True, False, True),
        ("I am not available to work on the capstone presentation this evening.", "academic_student", "chat", True, False, True),
        ("I won't be able to pick up the dry cleaning before the shop closes.", "personal_errands", "chat", False, False, True),
        ("I declined to take responsibility for the staging server maintenance.", "engineering", "slack", False, False, True),
        ("We won't deploy to production on a Friday afternoon under any circumstances.", "engineering", "slack", True, False, False),
        ("I am not going to attend the optional retrospective session tomorrow.", "project", "chat", True, False, True),
        ("I refuse to work through the weekend to finish these marketing banners.", "operations", "chat", True, False, True),
        ("I haven't committed to reviewing Arjun's pull request today.", "engineering", "slack", True, False, True),
        ("I cannot deliver the hardware inventory sheet without warehouse access.", "operations", "ticket", False, True, True),
        ("I won't promise something that our engineering team cannot deliver.", "sales_client", "email", False, False, True),
        ("I am not going to share unverified benchmarks with the customer.", "sales_client", "slack", False, False, True),
        ("We will definitely not finish the entire migration within this sprint.", "engineering", "meeting_transcript", False, False, False),
        ("I am not responsible for preparing the meeting minutes for today's sync.", "operations", "chat", True, False, True),
        ("I won't be writing the documentation unless given allocated sprint points.", "engineering", "ticket", False, True, True),
        ("I didn't say I would submit the expense reports before noon.", "operations", "chat", True, False, True),
        ("I am not promising any delivery date until the vendor ships the parts.", "operations", "email", False, True, True),
        ("I won't be joining the customer escalation call at 8 PM tonight.", "sales_client", "slack", True, False, True),
        ("We have decided not to roll out the updated UI this week.", "project", "slack", True, False, False),
        ("I cannot sign the vendor contract without legal review.", "executive", "email", False, True, True),
        ("I'm definitely not handling customer support chats over the holiday.", "operations", "chat", False, False, True),
        ("I won't fix this bug until you provide a reproducible test case.", "engineering", "ticket", False, True, True),
        ("I am not going to send the preliminary numbers to the board.", "executive", "chat", False, False, True),
        ("We didn't promise to deliver thirty feature points this sprint.", "project", "meeting_transcript", False, False, False),
        ("I am refusing to approve the budget increase without clear justification.", "executive", "email", False, True, True),
        ("I won't be present at the lab to run the overnight experiment.", "academic_student", "chat", True, False, True),
    ]
    for n, dom, src, dl, cond, owner in negations:
        items.append({
            "text": n,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Direct negation, refusal, or statement disclaiming commitment or responsibility."
        })

    # Category D: Requests, Imperatives & Prompts Directed at Others (35 examples)
    requests = [
        ("Please make sure you submit the quarterly tax documents before 5 PM.", "operations", "email", True, False, False),
        ("Kindly send over the updated wireframes as soon as you get a chance.", "project", "slack", False, False, False),
        ("Make sure to push your branch and open a PR before taking off today.", "engineering", "slack", True, False, False),
        ("Can you please follow up with the logistics vendor regarding the tracking number?", "operations", "email", False, False, False),
        ("Ensure that the release notes are circulated to all stakeholders by tomorrow.", "project", "slack", True, False, False),
        ("Please deliver the revised budget spreadsheet to finance by Wednesday noon.", "operations", "email", True, False, False),
        ("Don't forget to attach the signed customer agreement before archiving the ticket.", "sales_client", "ticket", False, False, False),
        ("Take a look at the staging cluster alerts and let the team know what happened.", "engineering", "ticket", False, False, False),
        ("Please review the attached contract draft and reply with your comments.", "sales_client", "email", False, False, False),
        ("Remember to submit your self-evaluation form before Friday 5 PM.", "operations", "slack", True, False, False),
        ("Hey Rahul, please deploy the hotfix patch to staging as soon as possible.", "engineering", "chat", False, False, False),
        ("Could you please send the zoom link for our meeting tomorrow morning?", "personal_errands", "chat", True, False, False),
        ("Make sure the client proposal includes our standard terms and conditions.", "sales_client", "email", False, False, False),
        ("Please upload the recorded user testing session to the shared drive.", "project", "ticket", False, False, False),
        ("Forward the invoice breakdown to accounting when you receive it.", "operations", "chat", False, True, False),
        ("Be sure to back up the Postgres database before applying the schema changes.", "engineering", "ticket", False, True, False),
        ("Kindly confirm whether you will be attending the sprint planning meeting.", "project", "email", False, False, False),
        ("Please verify that all unit tests pass before submitting the PR.", "engineering", "slack", False, True, False),
        ("Don't forget to buy groceries on your way back from work tonight.", "personal_errands", "chat", True, False, False),
        ("Send me a copy of the quotation spreadsheet before you send it to the client.", "sales_client", "chat", False, True, False),
        ("Check the server logs to see if there are any 500 errors occurring.", "engineering", "slack", False, False, False),
        ("Please double-check the figures in the slide deck before the board meeting.", "executive", "email", False, False, False),
        ("Ensure the customer receives an automated confirmation email upon payment.", "operations", "ticket", False, False, False),
        ("Make sure you submit the group assignment before 11 PM tonight.", "academic_student", "chat", True, False, False),
        ("Please coordinate with the security auditor to grant them sandbox access.", "engineering", "email", False, False, False),
        ("Remember to turn off the test instances after completing the benchmark.", "engineering", "slack", False, True, False),
        ("Kindly provide feedback on the draft proposal by tomorrow afternoon.", "sales_client", "email", True, False, False),
        ("Please update the Jira status once you finish the code review.", "project", "chat", False, True, False),
        ("See to it that the release candidate is packaged before the freeze date.", "engineering", "slack", False, False, False),
        ("Do not push changes directly to the main branch without approval.", "engineering", "ticket", False, True, False),
        ("Please remind the customer about their overdue payment before Friday.", "sales_client", "email", True, False, False),
        ("Make sure to archive the old sprint retrospective board after today.", "project", "slack", True, False, False),
        ("Drop off the signed lease agreement at the property office today.", "personal_errands", "chat", True, False, False),
        ("Please look into why the automated tests failed on the develop branch.", "engineering", "slack", False, False, False),
        ("Send the revised presentation slides to the marketing director.", "executive", "chat", False, False, False),
    ]
    for r, dom, src, dl, cond, owner in requests:
        items.append({
            "text": r,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Directive or imperative requesting action from others; not a speaker commitment."
        })

    # Category E: Third-Party Reporting, Hearsay & Attribution (30 examples)
    hearsay = [
        ("Arjun told me he might submit the quotation by noon, but he didn't confirm.", "sales_client", "slack", True, False, True),
        ("According to Priya, the sales team was supposed to send the updated pricing yesterday.", "sales_client", "chat", False, False, True),
        ("The manager said John is going to handle the staging environment configuration.", "engineering", "meeting_transcript", False, False, True),
        ("Elena mentioned during standup that Marcus will probably review the draft.", "project", "slack", False, False, True),
        ("I heard from Sneha that the offshore team is delivering the patch tomorrow.", "engineering", "chat", True, False, True),
        ("David claimed he would complete the security review, though nobody verified it.", "engineering", "ticket", False, False, True),
        ("The client representative said they would send us the API credentials soon.", "sales_client", "email", False, False, True),
        ("Word around the office is that the platform squad will fix the latency bug.", "engineering", "chat", False, False, False),
        ("Neha told the team that Vikram had already submitted the report.", "operations", "slack", False, False, True),
        ("Someone said the DevOps team was planning to restart the worker nodes tonight.", "engineering", "slack", True, False, False),
        ("Alex informed us that the marketing agency will provide the assets next week.", "operations", "email", True, False, True),
        ("The professor announced that the TA will grade the lab submissions by Friday.", "academic_student", "slack", True, False, True),
        ("Chen mentioned that his team might push the release candidate on Thursday.", "engineering", "chat", True, False, True),
        ("According to the support lead, the customer agreed to test the workaround.", "operations", "ticket", False, False, True),
        ("Rahul said he thought Priya was preparing the financial forecast.", "operations", "meeting_transcript", False, False, True),
        ("The contractor stated they had completed the initial phase of the audit.", "executive", "email", False, False, True),
        ("The vendor claims they sent the replacement hardware yesterday afternoon.", "operations", "ticket", False, False, True),
        ("Our product owner said the feature rollout was scheduled for next sprint.", "project", "slack", False, False, True),
        ("Kavya mentioned that she saw Arjun working on the database scripts.", "engineering", "chat", False, False, True),
        ("The customer reported that the system threw an error during checkout.", "engineering", "ticket", False, False, True),
        ("Marcus told me Elena is the one responsible for the pitch deck.", "executive", "chat", False, False, True),
        ("According to the schedule, the cleaning service visits every Tuesday.", "personal_errands", "chat", False, False, False),
        ("Sneha said she believes the invoice was paid last week.", "operations", "email", False, False, True),
        ("The newsletter stated that the conference registration closes tomorrow.", "academic_student", "email", True, False, False),
        ("John mentioned that the backend team had already deployed the fix.", "engineering", "slack", False, False, True),
        ("The account executive said the prospect would sign before month-end.", "sales_client", "meeting_transcript", True, False, True),
        ("Priya told the group that Vikram promised to bring the presentation clicker.", "academic_student", "chat", False, False, True),
        ("Rumor has it that the infrastructure team will migrate to Kubernetes.", "engineering", "chat", False, False, False),
        ("The recruiter told me the hiring manager would review my resume tomorrow.", "personal_errands", "email", True, False, True),
        ("Arjun said he assumed someone else had updated the project timeline.", "project", "slack", False, False, True),
    ]
    for h, dom, src, dl, cond, owner in hearsay:
        items.append({
            "text": h,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Third-party hearsay or report describing past/external actions rather than an active commitment."
        })

    # Category F: Habitual, Procedural & General Statements (15 examples)
    habitual = [
        ("Our engineering department deploys microservice updates every Tuesday morning.", "engineering", "slack", False, False, False),
        ("We typically send client performance invoices on the first of every month.", "sales_client", "email", False, False, False),
        ("Standard operating procedure requires submitting all expense receipts within 48 hours.", "operations", "ticket", True, False, False),
        ("The nightly backup job archives the database cluster at 2 AM every day.", "engineering", "ticket", True, False, False),
        ("Customer success sends a satisfaction survey 3 days after ticket resolution.", "operations", "email", False, False, False),
        ("Sprint retrospectives are held bi-weekly on alternating Thursdays.", "project", "slack", False, False, False),
        ("In our team, the on-call engineer monitors the error dashboard around the clock.", "engineering", "slack", False, False, False),
        ("The library closes at 10 PM on weekdays during final exams.", "academic_student", "chat", True, False, False),
        ("Client agreements are usually reviewed by legal before signing.", "executive", "email", False, False, False),
        ("All pull requests require two peer approvals before merging into main.", "engineering", "slack", False, False, False),
        ("The finance department reconciles payroll on the twenty-fifth of each month.", "operations", "meeting_transcript", True, False, False),
        ("We always conduct postmortems following severe production outages.", "engineering", "ticket", False, False, False),
        ("Team standups run from 9:30 AM to 9:45 AM every weekday.", "project", "chat", True, False, False),
        ("The university portal locks course registration at midnight on Sunday.", "academic_student", "email", True, False, False),
        ("Quarterly OKR scoring occurs during the first week of each new quarter.", "executive", "meeting_transcript", False, False, False),
    ]
    for hb, dom, src, dl, cond, owner in habitual:
        items.append({
            "text": hb,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "professional",
            "source_type": src,
            "reason": "General descriptive statement explaining routine, policy, or recurring schedule."
        })

    # Category G: Hypothetical & Counterfactual Statements (10 examples)
    hypotheticals = [
        ("If we had more headcount, we could have finalized the mobile wireframes this week.", "project", "meeting_transcript", True, True, False),
        ("Had the client replied earlier, I would have sent the proposal this morning.", "sales_client", "email", True, True, True),
        ("If I were in charge of DevOps, I would deploy the hotfix immediately.", "engineering", "slack", False, True, True),
        ("Even if they ask, I wouldn't recommend promising delivery before next quarter.", "executive", "meeting_transcript", True, True, True),
        ("Unless management allocates emergency budget, nobody is working on this migration.", "engineering", "slack", False, True, False),
        ("If it weren't raining so heavily, I might have gone to the grocery store today.", "personal_errands", "chat", True, True, True),
        ("If only the CI pipeline hadn't crashed, the release would have gone out at noon.", "engineering", "chat", True, True, False),
        ("Were I available this evening, I would happily help you review the paper draft.", "academic_student", "chat", True, True, True),
        ("If the contract terms had been acceptable, we would have signed yesterday.", "sales_client", "email", False, True, False),
        ("Unless someone steps up to lead the squad, this feature will sit in backlog.", "project", "slack", False, True, False),
    ]
    for hp, dom, src, dl, cond, owner in hypotheticals:
        items.append({
            "text": hp,
            "label": "NON_COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Counterfactual or unfulfilled hypothetical statement without active commitment."
        })

    assert len(items) == 220, f"Expected 220 non-commitments, got {len(items)}"
    return items


def build_hard_commitments() -> List[Dict]:
    """Builds 220 difficult COMMITMENT examples."""
    items = []

    # Category H1: Direct First-Person Strong Commitments with Deadlines & Deliverables (45 examples)
    direct_commitments = [
        ("I will personally email the revised vendor agreement before 4 PM today.", "sales_client", "email", True, False, True),
        ("I'll finish and push the database migration scripts by tonight at 9 PM.", "engineering", "slack", True, False, True),
        ("I am going to deliver the sprint retrospective summary before tomorrow's all-hands.", "project", "chat", True, False, True),
        ("I'll prepare the final budget breakdown for finance first thing tomorrow morning.", "operations", "slack", True, False, True),
        ("I will upload the high-fidelity mockups to Figma before end of day Wednesday.", "project", "ticket", True, False, True),
        ("I commit to resolving all critical Sentry errors before tomorrow's launch.", "engineering", "slack", True, False, True),
        ("I'll have the client quotation spreadsheet drafted and sent before 1 PM today.", "sales_client", "chat", True, False, True),
        ("I am definitely deploying the authentication hotfix before the evening peak.", "engineering", "slack", True, False, True),
        ("I promise to complete the code review on your pull request before 5 PM.", "engineering", "chat", True, False, True),
        ("I will draft and publish the post-incident review document by Friday noon.", "engineering", "ticket", True, False, True),
        ("I'll submit our capstone research methodology section to the professor tonight.", "academic_student", "email", True, False, True),
        ("I am going to finalize the investor slide deck before our sync tomorrow at 10 AM.", "executive", "chat", True, False, True),
        ("I will send you the finalized flight itinerary before I leave the office today.", "personal_errands", "chat", True, False, True),
        ("I'll compile and distribute the weekly operations KPI dashboard by Monday morning.", "operations", "email", True, False, True),
        ("I will configure the Redis caching layer on staging before the QA team starts testing.", "engineering", "slack", False, True, True),
        ("I'll write the integration tests for the Stripe webhook endpoints tonight.", "engineering", "ticket", True, False, True),
        ("I am going to send the signed nondisclosure agreement to their legal team by 3 PM.", "sales_client", "email", True, False, True),
        ("I promise to look through your thesis draft and add inline comments by Sunday evening.", "academic_student", "chat", True, False, True),
        ("I'll deliver the revised pricing proposal to the enterprise prospect before EOD.", "sales_client", "slack", True, False, True),
        ("I will personally verify the customer refund records before closing the ticket.", "operations", "ticket", False, False, True),
        ("I'll create the wireframe user flow diagrams for the onboarding revamp by Thursday.", "project", "ticket", True, False, True),
        ("I am going to push the performance benchmark numbers to the repository before 6 PM.", "engineering", "slack", True, False, True),
        ("I'll coordinate with the data center engineers to complete the hardware upgrade tonight.", "operations", "email", True, False, True),
        ("I will finish grading the undergraduate midterms before Friday afternoon.", "academic_student", "chat", True, False, True),
        ("I'll send the contractor their updated statement of work before 11 AM tomorrow.", "operations", "email", True, False, True),
        ("I am going to deliver the customer feedback summary to the design squad by Wednesday.", "project", "slack", True, False, True),
        ("I will make sure the release candidate build is tagged and uploaded before midnight.", "engineering", "slack", True, False, True),
        ("I'll prepare the executive summary for the quarterly board review before Thursday morning.", "executive", "chat", True, False, True),
        ("I will fix the mobile responsiveness glitch on the checkout page before tomorrow's demo.", "engineering", "ticket", True, False, True),
        ("I'll send you the apartment lease agreement scanned copy before 2 PM today.", "personal_errands", "chat", True, False, True),
        ("I am going to conduct the candidate technical interview at 3 PM as scheduled.", "operations", "slack", True, False, True),
        ("I will complete the API rate limiting implementation before our release freeze.", "engineering", "ticket", False, True, True),
        ("I'll write and send the newsletter recap to our subscriber list by Friday 10 AM.", "operations", "email", True, False, True),
        ("I am going to audit our cloud spending and present cost reduction recommendations on Monday.", "executive", "meeting_transcript", True, False, True),
        ("I will deploy the database index optimizations tonight during the maintenance window.", "engineering", "slack", True, False, True),
        ("I'll prepare the laboratory experiment apparatus before tomorrow's 9 AM session.", "academic_student", "chat", True, False, True),
        ("I am going to review the Master Services Agreement redlines before noon tomorrow.", "sales_client", "email", True, False, True),
        ("I'll deliver the sprint burndown analysis to the engineering director by Friday EOD.", "project", "slack", True, False, True),
        ("I will send the team the updated architectural diagram before the design sync at 2 PM.", "engineering", "chat", True, False, True),
        ("I'll submit the annual tax filings before the accountant's deadline on Wednesday.", "personal_errands", "email", True, False, True),
        ("I am going to handle the customer data export request before 4 PM today.", "operations", "ticket", True, False, True),
        ("I will complete the Docker containerization for the microservices before end of sprint.", "engineering", "ticket", False, False, True),
        ("I'll email the client meeting notes and action items within two hours after the call.", "sales_client", "email", True, False, True),
        ("I am going to push the hotfix for the broken navigation bar before lunch today.", "engineering", "slack", True, False, True),
        ("I will personally supervise the production database cutover tomorrow night at 11 PM.", "engineering", "meeting_transcript", True, False, True),
    ]
    for d, dom, src, dl, cond, owner in direct_commitments:
        items.append({
            "text": d,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "medium",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "professional",
            "source_type": src,
            "reason": "Direct explicit first-person commitment with concrete deliverable and timeframe."
        })

    # Category H2: Idiomatic, Colloquial & Conversational Undertakings (45 examples)
    colloquial_commitments = [
        ("Count on me to wrap up the API integration before the demo tomorrow.", "engineering", "slack", True, False, True),
        ("Consider it done, I'll send the client deck before 5 PM.", "executive", "chat", True, False, True),
        ("I'm on it — will have the bug triage report ready for the team within two hours.", "engineering", "slack", True, False, True),
        ("I'll take care of drafting the incident postmortem by Friday afternoon.", "engineering", "ticket", True, False, True),
        ("Leave the quarterly OKR alignment deck with me; I'll finish it tonight.", "executive", "chat", True, False, True),
        ("I've got this covered; I'll submit the staging deployment checklist before noon.", "engineering", "slack", True, False, True),
        ("I'm locking myself in to finish the test automation suite by Monday morning.", "engineering", "chat", True, False, True),
        ("Putting my name down to handle the security remediation tasks by Thursday.", "engineering", "ticket", True, False, True),
        ("Rest assured, I'll make sure the release notes go out before the client sync.", "project", "slack", True, False, True),
        ("No worries at all, I will deliver the spreadsheet before our 3 PM meeting.", "operations", "chat", True, False, True),
        ("You can rely on me to get the quotation sent out before the end of the day.", "sales_client", "email", True, False, True),
        ("I'm taking ownership of the customer refund processing starting right now.", "operations", "slack", False, False, True),
        ("I'll own this task and make sure the database migration completes tonight.", "engineering", "slack", True, False, True),
        ("Consider the slide deck finished; I'm wrapping up the final charts right now.", "executive", "chat", False, False, True),
        ("I'll step up and draft the API documentation before tomorrow's review.", "engineering", "slack", True, False, True),
        ("Don't stress, I'm handling the contract redlines and will send them today.", "sales_client", "email", True, False, True),
        ("I'll make sure the PR gets reviewed and approved before the build starts tonight.", "engineering", "slack", True, False, True),
        ("On it! I'll ping the client with our revised proposal before noon.", "sales_client", "chat", True, False, True),
        ("I've got the presentation covered, will share the link before our morning call.", "project", "slack", True, False, True),
        ("Taking care of the staging database cleanup right away.", "engineering", "ticket", False, False, True),
        ("I'll make sure this gets pushed before the deadline without fail.", "engineering", "chat", False, False, True),
        ("You have my word, I will send the revised quote before 4 PM today.", "sales_client", "email", True, False, True),
        ("I will personally see to it that the release candidate is deployed before midnight.", "executive", "slack", True, False, True),
        ("I am taking full responsibility for finishing the thesis literature review by Sunday.", "academic_student", "chat", True, False, True),
        ("Leave it to me, I'll compile the customer survey results before Friday.", "project", "slack", True, False, True),
        ("I'm on top of it; I'll submit the bug fix patch before lunch.", "engineering", "ticket", True, False, True),
        ("Count me in for handling the on-call pager shift over the weekend.", "engineering", "slack", True, False, True),
        ("I'll see this through and guarantee the invoice breakdown is delivered today.", "operations", "chat", True, False, True),
        ("Consider it handled; I will email the revised timeline to the client before 5 PM.", "sales_client", "email", True, False, True),
        ("I'll jump on this immediately and have the wireframes ready by tomorrow morning.", "project", "chat", True, False, True),
        ("I promise I'll get the lab experiment results charted before midnight tonight.", "academic_student", "chat", True, False, True),
        ("I'm committing to delivering the pitch deck revisions before the investor pitch.", "executive", "slack", False, True, True),
        ("Rest easy, I'll take care of updating the DNS records tonight.", "engineering", "ticket", True, False, True),
        ("I will make certain that the vendor receives the signed contract before 3 PM.", "operations", "email", True, False, True),
        ("I'll take the lead on this and deliver the architecture draft before Friday.", "engineering", "meeting_transcript", True, False, True),
        ("I've claimed this ticket and will push the fix before the end of the sprint.", "engineering", "ticket", False, False, True),
        ("Don't worry about the slides, I'll polish them up tonight before the demo.", "executive", "chat", True, False, True),
        ("I am definitely taking care of the customer escalation tickets before I sign off.", "operations", "slack", False, False, True),
        ("I'll guarantee that the data export is delivered to compliance before Friday noon.", "operations", "email", True, False, True),
        ("I'm locking this into my calendar and will submit the draft before tomorrow 10 AM.", "academic_student", "chat", True, False, True),
        ("I will ensure the automated backup script is restored before the night shift.", "engineering", "slack", False, True, True),
        ("Leave the code review to me; I will approve the changes before 6 PM.", "engineering", "slack", True, False, True),
        ("I am on track and will deliver the financial audit response before tomorrow EOD.", "operations", "email", True, False, True),
        ("I will see that the client receives our pricing tiers before close of business.", "sales_client", "email", True, False, True),
        ("Trust me on this, I'll have the hotfix merged before the staging run at 4 PM.", "engineering", "chat", True, False, True),
    ]
    for c, dom, src, dl, cond, owner in colloquial_commitments:
        items.append({
            "text": c,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Conversational or idiomatic commitment expressing clear, affirmative undertaking by speaker."
        })

    # Category H3: Multi-Sentence Conversational Undertakings (40 examples)
    multi_sentence = [
        ("Thanks for flagging the issue. I am looking into the payment gateway error right now and will deploy a hotfix before 6 PM.", "engineering", "slack", True, False, True),
        ("I understand the urgency. I will compile the audit logs and email them to compliance by tomorrow morning.", "operations", "email", True, False, True),
        ("Good catch on the broken styling. I'll fix the CSS layout and push the PR within the next hour.", "engineering", "slack", True, False, True),
        ("I saw your message about the customer escalations. I'll take full ownership of resolving them before end of day.", "operations", "chat", True, False, True),
        ("We discussed this in the sync earlier. I will draft the RFC and share the link with the team by Thursday EOD.", "engineering", "slack", True, False, True),
        ("I received the revised requirements from the client. I'll update the project scope spreadsheet before tomorrow noon.", "project", "email", True, False, True),
        ("Sorry for the delay on this. I am finalizing the financial forecast and will send it over tonight before midnight.", "operations", "chat", True, False, True),
        ("I know the demo is tomorrow. Rest assured, I will have the prototype fully functional before our 9 AM prep call.", "engineering", "slack", True, False, True),
        ("The numbers look mostly solid. I'll make the requested adjustments to the pitch deck and email the new version today.", "executive", "email", True, False, True),
        ("I noticed the broken unit tests on main. I will investigate the root cause and push a fix before 2 PM.", "engineering", "slack", True, False, True),
        ("Thanks for the feedback on chapter three. I'll incorporate your suggestions and share the revised draft by Sunday.", "academic_student", "chat", True, False, True),
        ("I understand the client is waiting. I will call their procurement lead before 4 PM today to clarify the terms.", "sales_client", "email", True, False, True),
        ("Great point about the database indexes. I will benchmark the queries and apply the migration script tonight.", "engineering", "ticket", True, False, True),
        ("I'm aware of the impending audit deadline. I will ensure all compliance documentation is uploaded before Friday.", "operations", "slack", True, False, True),
        ("I saw that Arjun is out sick today. I will step in to cover his deployment duties tonight.", "engineering", "chat", True, False, True),
        ("Thank you for reviewing the wireframes. I'll refine the checkout interaction and update the Figma file by tomorrow.", "project", "ticket", True, False, True),
        ("I know the sprint ends tomorrow. I am committed to completing the rest of my tickets before the sprint review.", "project", "slack", True, False, True),
        ("The server memory spike looks concerning. I'll profile the worker processes and share my findings before 5 PM.", "engineering", "slack", True, False, True),
        ("I received the hardware delivery confirmation. I will unbox and configure the staging cluster before Wednesday noon.", "operations", "email", True, False, True),
        ("I see what went wrong with the billing calculation. I will write a patch and deploy it to production before midnight.", "engineering", "ticket", True, False, True),
        ("I talked with the designer about the color tokens. I'll update the frontend theme and open a PR by Thursday.", "engineering", "slack", True, False, True),
        ("The client requested an extra review round. I will schedule a walkthrough with them before the end of the week.", "sales_client", "email", True, False, True),
        ("I understand your concern about code quality. I will write comprehensive unit tests for this module before merging.", "engineering", "ticket", False, True, True),
        ("Thanks for the reminder about the tax form. I will fill it out and drop it off at the accounting office today.", "personal_errands", "chat", True, False, True),
        ("I reviewed the initial customer complaint. I'll reach out to the user directly and resolve the issue before 3 PM.", "operations", "ticket", True, False, True),
        ("I know you're blocked on the schema design. I will finish drafting the tables and ping you within the hour.", "engineering", "chat", True, False, True),
        ("We need to submit the grant application soon. I will draft the executive narrative and send it to you by Tuesday.", "academic_student", "email", True, False, True),
        ("I saw the notification about the failing webhook. I will inspect the payload logs and deploy a hotfix before 6 PM.", "engineering", "slack", True, False, True),
        ("The contract redlines are mostly acceptable. I'll make the final legal tweaks and email the counter-proposal today.", "sales_client", "email", True, False, True),
        ("I understand the team needs these assets. I'll export all high-res graphics and upload them to Drive before 4 PM.", "project", "slack", True, False, True),
        ("I know the staging environment has been unstable. I will rebuild the container images and verify stability tonight.", "engineering", "ticket", True, False, True),
        ("Thanks for clarifying the user story requirements. I will start the implementation and have a draft PR ready tomorrow.", "engineering", "slack", True, False, True),
        ("I hear your frustration regarding the invoice delay. I will personally escalate this to accounting before noon.", "sales_client", "chat", True, False, True),
        ("I see that the regression suite uncovered two bugs. I will fix both issues and trigger a rebuild before 7 PM.", "engineering", "ticket", True, False, True),
        ("I agree that we need better logging. I will add structured log tracing to the checkout service before Friday.", "engineering", "slack", True, False, True),
        ("Thanks for sending the lecture notes. I will compile our group study guide and share it before Saturday morning.", "academic_student", "chat", True, False, True),
        ("I understand the importance of this enterprise deal. I will ensure our solutions architect replies to their RFP by Monday.", "sales_client", "email", True, False, True),
        ("I saw your pull request notification. I'm finishing my current task now and will review your code before 5 PM.", "engineering", "slack", True, False, True),
        ("The customer requested custom onboarding documentation. I will write the walkthrough guide and share it before Wednesday.", "operations", "email", True, False, True),
        ("I know the release notes are required for the launch. I'll gather the changelog items and publish the doc tomorrow morning.", "project", "slack", True, False, True),
    ]
    for m, dom, src, dl, cond, owner in multi_sentence:
        items.append({
            "text": m,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "hard",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "conversational",
            "source_type": src,
            "reason": "Multi-sentence conversational message concluding with a clear, direct commitment to act."
        })

    # Category H4: Conditional Commitments with Concrete Undertakings (35 examples)
    conditionals = [
        ("As soon as the build pipeline goes green, I will merge and deploy the staging artifacts.", "engineering", "slack", False, True, True),
        ("Once Arjun approves the database schema changes, I'll run the migration script immediately.", "engineering", "slack", False, True, True),
        ("If the client signs the order form today, I will trigger onboarding before 5 PM.", "sales_client", "email", True, True, True),
        ("Assuming we get the Figma assets by noon, I'll implement the hero section tonight.", "engineering", "chat", True, True, True),
        ("Provided finance releases the voucher, I'll process the vendor payment before end of day.", "operations", "email", True, True, True),
        ("If QA gives the green light by 3 PM, I will push the release candidate to production tonight.", "engineering", "slack", True, True, True),
        ("Once you send over the raw CSV data, I'll generate the visualization charts within two hours.", "project", "chat", True, True, True),
        ("As soon as legal returns the redlined contract, I will forward it to the vendor counsel.", "sales_client", "email", False, True, True),
        ("If the customer accepts the proposed SLA, I will draft the formal addendum by tomorrow.", "sales_client", "email", True, True, True),
        ("Once the staging server reboot completes, I will verify the API health endpoints.", "engineering", "ticket", False, True, True),
        ("Assuming Arjun finishes the PR review by 4 PM, I will merge it and tag the release.", "engineering", "slack", True, True, True),
        ("If you can share the meeting recording, I'll write up the transcript and action items tonight.", "project", "chat", True, True, True),
        ("As soon as my flight lands, I will email the revised slide deck to the board.", "executive", "email", False, True, True),
        ("Provided the unit tests pass on CI, I'll trigger the canary rollout before 6 PM.", "engineering", "slack", True, True, True),
        ("Once we receive the hardware samples, I will benchmark the sensor latency by Friday.", "engineering", "ticket", True, True, True),
        ("If Neha approves the budget estimate, I'll issue the purchase order before tomorrow noon.", "operations", "slack", True, True, True),
        ("As soon as the DNS propagation finishes, I will test the SSL certificate setup.", "engineering", "ticket", False, True, True),
        ("Assuming the customer confirms the appointment, I will conduct the onboarding call tomorrow at 11 AM.", "sales_client", "email", True, True, True),
        ("If the professor approves our thesis topic, I will draft the project abstract before Monday.", "academic_student", "chat", True, True, True),
        ("Once the payment gateway confirms the refund, I will notify the customer via email.", "operations", "ticket", False, True, True),
        ("Provided that Arjun shares his code branch, I'll integrate the search endpoints tonight.", "engineering", "slack", True, True, True),
        ("If the weather permits tomorrow, I'll drop by the warehouse to inspect the inventory.", "personal_errands", "chat", True, True, True),
        ("As soon as the design system tokens are published, I will update our component library.", "engineering", "slack", False, True, True),
        ("Once the contract is fully executed, I will circulate copies to all executive stakeholders.", "executive", "email", False, True, True),
        ("Assuming the staging tests pass without error, I will schedule the maintenance window for Tuesday.", "engineering", "ticket", True, True, True),
        ("If you send me the hotel booking confirmation, I'll arrange the airport pickup tonight.", "personal_errands", "chat", True, True, True),
        ("Once the data migration finishes, I will validate the user table integrity before 10 AM.", "engineering", "slack", True, True, True),
        ("Provided we get stakeholder sign-off today, I will start development on the feature tomorrow morning.", "project", "meeting_transcript", True, True, True),
        ("If the security scan reports zero critical flaws, I'll approve the pull request immediately.", "engineering", "ticket", False, True, True),
        ("As soon as the client deposits the initial retainer, I will begin the architecture phase.", "sales_client", "email", False, True, True),
        ("Once Priya uploads her chapter notes, I will compile the complete research document tonight.", "academic_student", "chat", True, True, True),
        ("If the backend API is ready by Thursday, I will wire up the dashboard UI before the sprint demo.", "engineering", "slack", True, True, True),
        ("Assuming finance clears the invoice, I will send the software license keys to the client today.", "operations", "email", True, True, True),
        ("Once the code freeze takes effect, I will run the full regression suite overnight.", "engineering", "slack", True, True, True),
        ("If you can confirm the headcount requirements, I will publish the job descriptions before Friday.", "operations", "email", True, True, True),
    ]
    for cd, dom, src, dl, cond, owner in conditionals:
        items.append({
            "text": cd,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "medium",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "professional",
            "source_type": src,
            "reason": "Conditional commitment triggered upon condition fulfillment, promising concrete action."
        })

    # Category H5: Team & First-Person Plural Firm Undertakings (25 examples)
    team_commitments = [
        ("We will deliver the updated sprint backlog spreadsheet to the director by tomorrow noon.", "project", "slack", True, False, True),
        ("Our team commits to completing the penetration testing report before Friday.", "engineering", "email", True, False, True),
        ("We are going to finalize the onboarding walkthrough slides before the customer workshop.", "project", "chat", False, False, True),
        ("We promise to deploy the new search indexing pipeline before the weekend.", "engineering", "slack", True, False, True),
        ("Our squad will resolve all blocker issues on the checkout page before the flash sale.", "engineering", "ticket", False, True, True),
        ("We will present the quarterly financial review to executive leadership on Monday morning.", "operations", "meeting_transcript", True, False, True),
        ("We commit to reducing API response latency by 20 percent before the next release cycle.", "engineering", "meeting_transcript", False, False, True),
        ("Our team is going to conduct full user acceptance testing before the client handover.", "project", "email", False, True, True),
        ("We will submit our group capstone deliverable to the portal before the 11 PM deadline.", "academic_student", "slack", True, False, True),
        ("We promise to provide weekly status updates to all project stakeholders every Friday.", "project", "email", True, False, True),
        ("Our department will ensure all employees complete compliance training before month-end.", "operations", "email", True, False, True),
        ("We will publish the updated developer documentation before releasing the SDK.", "engineering", "ticket", False, True, True),
        ("Our infrastructure team commits to maintaining 99.9% uptime during the migration window.", "engineering", "ticket", False, False, True),
        ("We are going to roll out two-factor authentication to all staff accounts before next week.", "operations", "email", True, False, True),
        ("We will deliver the final architectural blueprint to the client by Wednesday EOD.", "engineering", "email", True, False, True),
        ("Our support squad will maintain 15-minute response times for critical escalations.", "operations", "slack", False, False, True),
        ("We are committed to delivering the core MVP features before the investor demo.", "executive", "meeting_transcript", False, True, True),
        ("We will audit all cloud storage buckets and restrict public access before Thursday.", "engineering", "slack", True, False, True),
        ("Our team will prepare the vendor comparison matrix and share it before tomorrow's sync.", "operations", "slack", True, False, True),
        ("We will deploy the updated privacy policy across all web properties before the deadline.", "operations", "ticket", False, False, True),
        ("We promise to thoroughly investigate the database deadlock issues before tomorrow.", "engineering", "slack", True, False, True),
        ("Our squad will deliver the revised sprint estimates by tomorrow at 10 AM.", "project", "slack", True, False, True),
        ("We will organize the customer focus group session before the end of the sprint.", "project", "meeting_transcript", False, False, True),
        ("We commit to delivering the automated billing reconciliation tool before next quarter.", "operations", "email", False, False, True),
        ("Our team will execute the disaster recovery drill this Saturday as planned.", "engineering", "email", True, False, True),
    ]
    for tm, dom, src, dl, cond, owner in team_commitments:
        items.append({
            "text": tm,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "medium",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "professional",
            "source_type": src,
            "reason": "Team-level firm undertaking binding group or department to concrete deliverable."
        })

    # Category H6: Student & Academic Project Commitments (15 examples)
    student_commitments = [
        ("I'll submit the distributed systems lab report to the portal before 11:59 PM tonight.", "academic_student", "chat", True, False, True),
        ("I'm going to finish writing Chapter 4 of our capstone thesis by Sunday evening.", "academic_student", "slack", True, False, True),
        ("I'll prepare the dataset charts and slides for our group presentation on Wednesday.", "academic_student", "chat", True, False, True),
        ("I will complete the math problem set and submit the PDF before tomorrow's class.", "academic_student", "chat", True, False, True),
        ("I'll run the machine learning model training overnight and share the accuracy graphs tomorrow.", "academic_student", "slack", True, False, True),
        ("I commit to drafting the literature review section for our conference paper by Friday.", "academic_student", "email", True, False, True),
        ("I am going to proofread our group submission before the turnitin deadline at midnight.", "academic_student", "chat", True, False, True),
        ("I will compile our benchmark code into a reproducible GitHub repo by Thursday.", "academic_student", "slack", True, False, True),
        ("I'll summarize the three research papers and email my notes to the study group tonight.", "academic_student", "email", True, False, True),
        ("I am going to meet with the teaching assistant tomorrow at 2 PM to debug our code.", "academic_student", "chat", True, False, True),
        ("I will finish the hardware simulation lab assignment before our Monday deadline.", "academic_student", "chat", True, False, True),
        ("I'll format our bibliography according to IEEE guidelines before submitting tonight.", "academic_student", "slack", True, False, True),
        ("I will record my 5-minute portion of our team video presentation by Friday noon.", "academic_student", "chat", True, False, True),
        ("I'm going to clean up the experimental data spreadsheet before our team sync tomorrow.", "academic_student", "chat", True, False, True),
        ("I will submit the revised thesis proposal to the committee chair before the deadline.", "academic_student", "email", False, False, True),
    ]
    for st, dom, src, dl, cond, owner in student_commitments:
        items.append({
            "text": st,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "medium",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "academic",
            "source_type": src,
            "reason": "Student or academic milestone commitment with concrete deliverable."
        })

    # Category H7: Executive, Client & SLA Formal Commitments (15 examples)
    sla_commitments = [
        ("I will provide your procurement team with a revised formal quotation by 2 PM.", "sales_client", "email", True, False, True),
        ("I'll review the Master Services Agreement redlines and reply to your counsel by tomorrow EOD.", "sales_client", "email", True, False, True),
        ("I commit to issuing the SLA credit adjustment memo before the billing cycle closes.", "operations", "email", True, False, True),
        ("I will deliver the quarterly executive summary to the board of directors by Thursday 9 AM.", "executive", "email", True, False, True),
        ("I will personally guarantee that your support tickets receive senior engineering escalation within one hour.", "sales_client", "email", True, False, True),
        ("I'll schedule the executive briefing between our CTO and your leadership team before Friday.", "executive", "email", True, False, True),
        ("I commit to providing a dedicated customer success engineer for your account starting next month.", "sales_client", "email", True, False, True),
        ("I will send the finalized statement of work signed by our managing director before 5 PM.", "executive", "email", True, False, True),
        ("I'll deliver the comprehensive cybersecurity compliance report to your auditors before Monday.", "engineering", "email", True, False, True),
        ("I guarantee our team will deliver the custom analytics integration before the contract milestone.", "sales_client", "email", False, False, True),
        ("I will ensure the service level agreement credits are applied to your upcoming monthly invoice.", "operations", "email", False, False, True),
        ("I'll deliver the revised scope documentation signed by both parties before Wednesday noon.", "sales_client", "email", True, False, True),
        ("I commit to presenting our five-year technology roadmap at the executive summit next Tuesday.", "executive", "meeting_transcript", True, False, True),
        ("I will ensure your data migration is completed with zero downtime by our engineering team.", "sales_client", "email", False, False, True),
        ("I'll send the countersigned partnership agreement to your legal counsel before EOD today.", "executive", "email", True, False, True),
    ]
    for sl, dom, src, dl, cond, owner in sla_commitments:
        items.append({
            "text": sl,
            "label": "COMMITMENT",
            "domain": dom,
            "difficulty": "medium",
            "has_deadline": dl,
            "has_condition": cond,
            "has_owner": owner,
            "language_style": "professional",
            "source_type": src,
            "reason": "Formal executive, sales, or SLA commitment binding the speaker or organization."
        })

    assert len(items) == 220, f"Expected 220 commitments, got {len(items)}"
    return items


def generate_hard_dataset():
    """Generates and validates the hard augmentation dataset."""
    print("=" * 60)
    print("GENERATING PROMISEOS TARGETED HARD DATASET (ROUND 2)")
    print("=" * 60)

    non_commitments = build_hard_non_commitments()
    commitments = build_hard_commitments()

    all_items = non_commitments + commitments
    print(f"Total hard examples generated: {len(all_items)}")
    print(f"  COMMITMENT:     {len(commitments)}")
    print(f"  NON_COMMITMENT: {len(non_commitments)}")

    # Assign IDs
    # Shuffle with fixed seed for balanced split
    random.seed(RANDOM_SEED)
    random.shuffle(commitments)
    random.shuffle(non_commitments)

    # 320 for train (160 C, 160 NC), 120 for hard validation (60 C, 60 NC)
    hard_train_items = commitments[:160] + non_commitments[:160]
    hard_val_items = commitments[160:] + non_commitments[160:]

    random.shuffle(hard_train_items)
    random.shuffle(hard_val_items)

    for i, it in enumerate(hard_train_items):
        it["id"] = f"hard_train_{i+1:04d}"

    for i, it in enumerate(hard_val_items):
        it["id"] = f"hard_val_{i+1:04d}"

    full_items = hard_train_items + hard_val_items

    # Convert to DataFrames
    cols = [
        "id", "text", "label", "domain", "difficulty",
        "has_deadline", "has_condition", "has_owner",
        "language_style", "source_type", "reason"
    ]
    df_full = pd.DataFrame(full_items)[cols]
    df_train = pd.DataFrame(hard_train_items)[cols]
    df_val = pd.DataFrame(hard_val_items)[cols]

    # Verify no internal duplicate texts
    norm_texts = df_full["text"].str.strip().str.lower()
    duplicates = norm_texts[norm_texts.duplicated()].tolist()
    if duplicates:
        raise ValueError(f"Found internal duplicates in hard dataset: {duplicates}")

    # Check cross-leakage against existing core splits and hidden set
    print("\nVerifying zero data leakage against core datasets and hidden dataset...")
    train_file = DATASETS_DIR / "train" / "train.csv"
    val_file = DATASETS_DIR / "validation" / "validation.csv"
    test_file = DATASETS_DIR / "test" / "test.csv"
    hidden_file = DATASETS_DIR / "hidden" / "hidden_inputs.csv"

    existing_texts: Set[str] = set()
    for p in [train_file, val_file, test_file, hidden_file]:
        if p.exists():
            d = pd.read_csv(p)
            existing_texts.update(d["text"].str.strip().str.lower().tolist())

    hard_texts = set(norm_texts.tolist())
    overlap = hard_texts.intersection(existing_texts)
    if overlap:
        raise ValueError(f"LEAKAGE DETECTED! Overlapping texts found: {overlap}")
    print("  PASSED: 0 overlapping texts with any existing dataset (core or hidden)!")

    # Save to disk
    AUG_DIR.mkdir(parents=True, exist_ok=True)
    full_path = AUG_DIR / "hard_examples.csv"
    train_path = AUG_DIR / "hard_train.csv"
    val_path = AUG_DIR / "hard_validation.csv"

    df_full.to_csv(full_path, index=False, encoding="utf-8")
    df_train.to_csv(train_path, index=False, encoding="utf-8")
    df_val.to_csv(val_path, index=False, encoding="utf-8")

    print(f"\nFiles saved successfully:")
    print(f"  - Full hard dataset: {full_path} ({len(df_full)} rows)")
    print(f"  - Hard train split:  {train_path} ({len(df_train)} rows)")
    print(f"  - Hard val split:    {val_path} ({len(df_val)} rows)")
    print("=" * 60)


if __name__ == "__main__":
    generate_hard_dataset()
