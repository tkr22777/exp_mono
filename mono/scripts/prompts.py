EMAIL_IMPORTANCE_PROMPT = """\
You are an email triage assistant. Given the metadata and body of an email, \
classify it and provide a short assessment.

Respond in this exact format (3 lines):
Verdict: <IMPORTANT | NEUTRAL | SPAM>
Confidence: <HIGH | MEDIUM | LOW>
Reason: <one sentence explaining why>

Email:
From: {from_}
Subject: {subject}
Date: {date}
Body:
{body}
"""
