"""
Document classification pipeline using scikit-learn.
TfidfVectorizer + MultinomialNB classifier to auto-categorize uploaded PDFs
by topic before ingestion, improving retrieval accuracy by routing queries
to relevant document collections (Pinecone namespaces).

Categories: legal, medical, technical, financial, general
"""

import os
import joblib
import logging
import numpy as np
from typing import Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

# Path to pre-trained model
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "classifier_pipeline.joblib")

CATEGORIES = ["legal", "medical", "technical", "financial", "general"]

# Pre-trained classifier instance
_classifier: Pipeline = None


def _get_training_data() -> Tuple[list, list]:
    """Generate synthetic training data for document classification.

    In production, this would be replaced with real labeled document data.
    """
    training_texts = [
        # Legal documents
        "This agreement is entered into by and between the parties hereinafter referred to as the licensor and licensee",
        "The defendant is hereby ordered to appear before the court on the specified date for arraignment",
        "Pursuant to section 12 of the contract law, the indemnification clause shall remain in effect",
        "The plaintiff alleges breach of contract and seeks monetary damages in the amount specified",
        "Terms and conditions governing the use of services including liability limitations and dispute resolution",
        "Intellectual property rights patent trademark copyright infringement licensing agreement",
        "Legal compliance regulatory framework statutory obligations jurisdiction enforcement",
        "Attorney client privilege confidentiality disclosure subpoena deposition testimony",
        "Arbitration mediation settlement negotiation legal dispute resolution proceedings",
        "Corporate bylaws shareholder agreement board resolution merger acquisition due diligence",
        "Non-disclosure agreement confidential information trade secrets proprietary data protection",
        "Employment contract termination clause severance package non-compete agreement",
        "Lease agreement tenant landlord rental property terms conditions obligations",
        "Power of attorney legal representative authorization consent fiduciary duty",
        "Class action lawsuit damages compensation restitution injunctive relief",

        # Medical documents
        "Patient presents with acute respiratory distress requiring immediate intubation and ventilation",
        "The MRI scan reveals a 2cm lesion in the frontal lobe consistent with glioblastoma multiforme",
        "Prescribed metformin 500mg twice daily for management of type 2 diabetes mellitus",
        "Post-operative care includes wound management antibiotic prophylaxis and physical therapy",
        "Clinical trial results demonstrate significant reduction in tumor size with immunotherapy",
        "Blood pressure monitoring glucose levels hemoglobin A1C cholesterol lipid panel",
        "Surgical procedure laparoscopic cholecystectomy anesthesia recovery complications",
        "Patient history chronic conditions medications allergies family medical history",
        "Radiology report CT scan ultrasound diagnostic imaging pathology findings",
        "Vaccination immunization schedule pediatric healthcare preventive medicine screening",
        "Mental health assessment anxiety depression cognitive behavioral therapy treatment plan",
        "Emergency department triage vital signs trauma assessment acute care protocol",
        "Pharmaceutical drug interactions dosage contraindications side effects pharmacology",
        "Epidemiology disease outbreak infection control public health surveillance",
        "Rehabilitation physical therapy occupational therapy recovery functional assessment",

        # Technical documents
        "The microservice architecture implements REST API endpoints with OAuth2 authentication",
        "Database schema migration includes adding indexes for query optimization and partitioning",
        "Kubernetes deployment configuration with horizontal pod autoscaling and load balancing",
        "The neural network model achieves 95% accuracy using transformer architecture with attention mechanism",
        "CI/CD pipeline integrates automated testing code review and container deployment",
        "Cloud infrastructure AWS EC2 S3 Lambda serverless computing scalability",
        "Software engineering design patterns object oriented programming SOLID principles",
        "Machine learning deep learning natural language processing computer vision algorithms",
        "Network security firewall encryption SSL TLS protocol vulnerability assessment",
        "Version control Git branching strategy merge conflict code repository management",
        "API documentation endpoint specification request response schema validation",
        "Frontend development React Angular Vue JavaScript TypeScript component architecture",
        "Backend development Python Java Node.js database ORM query optimization",
        "DevOps infrastructure as code Terraform Docker containerization orchestration",
        "Data engineering ETL pipeline data warehouse analytics processing streaming",

        # Financial documents
        "Quarterly earnings report shows 15% revenue growth with EBITDA margin improvement",
        "Portfolio diversification strategy includes allocation across equities bonds and commodities",
        "The balance sheet reflects total assets of $500 million with a debt-to-equity ratio of 0.8",
        "Tax filing requirements for fiscal year including deductions credits and estimated payments",
        "Investment analysis risk assessment return on investment capital allocation strategy",
        "Annual budget forecast expenditure revenue projection cash flow statement",
        "Stock market trading securities equity derivatives options futures commodities",
        "Banking mortgage loan interest rate credit score underwriting approval process",
        "Insurance premium coverage deductible claim settlement actuarial risk assessment",
        "Audit financial statement compliance GAAP IFRS accounting standards reporting",
        "Venture capital private equity startup funding valuation term sheet due diligence",
        "Cryptocurrency blockchain digital assets decentralized finance tokenomics",
        "Retirement planning pension 401k IRA social security annuity wealth management",
        "Mergers acquisitions corporate finance leveraged buyout synergy integration",
        "Foreign exchange currency trading international finance balance of payments",

        # General documents
        "Meeting notes from the quarterly planning session discussing project milestones and deadlines",
        "The research paper examines the impact of climate change on biodiversity in tropical regions",
        "Company newsletter highlights employee achievements community events and upcoming activities",
        "Standard operating procedures for workplace safety emergency evacuation and fire drills",
        "Annual report summarizing organizational achievements strategic goals and future plans",
        "Training manual onboarding guide employee handbook policies procedures guidelines",
        "Project proposal timeline deliverables stakeholders resource allocation objectives",
        "Communication memo internal announcement organizational update department changes",
        "Event planning conference workshop seminar agenda schedule logistics coordination",
        "Customer feedback survey satisfaction analysis service improvement recommendations",
        "Marketing strategy brand awareness content creation social media campaign analytics",
        "Product roadmap feature specification user story acceptance criteria sprint planning",
        "Environmental sustainability green energy carbon footprint reduction recycling",
        "Education curriculum syllabus course outline learning objectives assessment",
        "Travel itinerary business trip accommodation transportation expense report",
    ]

    training_labels = (
        ["legal"] * 15
        + ["medical"] * 15
        + ["technical"] * 15
        + ["financial"] * 15
        + ["general"] * 15
    )

    return training_texts, training_labels


def train_classifier() -> Pipeline:
    """Train and save the document classifier pipeline."""
    texts, labels = _get_training_data()

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1,
            max_df=0.95,
        )),
        ("clf", MultinomialNB(alpha=0.1)),
    ])

    pipeline.fit(texts, labels)

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    logger.info(f"Classifier saved to {MODEL_PATH}")

    return pipeline


def load_classifier() -> Pipeline:
    """Load the pre-trained classifier, training if needed."""
    global _classifier
    if _classifier is not None:
        return _classifier

    if os.path.exists(MODEL_PATH):
        _classifier = joblib.load(MODEL_PATH)
        logger.info("Loaded pre-trained classifier")
    else:
        logger.info("No pre-trained model found, training classifier...")
        _classifier = train_classifier()

    return _classifier


def classify_document(text: str) -> Tuple[str, float]:
    """Classify a document's text content into a category.

    Args:
        text: Document text content

    Returns:
        Tuple of (category, confidence_score)
    """
    classifier = load_classifier()

    # Predict category
    prediction = classifier.predict([text])[0]

    # Get confidence score
    probabilities = classifier.predict_proba([text])[0]
    confidence = float(np.max(probabilities))

    logger.info(f"Classified document as '{prediction}' with {confidence:.2%} confidence")
    return prediction, confidence


def get_category_probabilities(text: str) -> dict:
    """Get probability distribution across all categories.

    Args:
        text: Document text content

    Returns:
        Dict mapping category names to probabilities
    """
    classifier = load_classifier()
    probabilities = classifier.predict_proba([text])[0]
    classes = classifier.classes_

    return {
        category: float(prob)
        for category, prob in zip(classes, probabilities)
    }
