# utils/prioritization.py
from models.huggingface_model import analyze_with_flan

def prioritize_requirements(requirements, responses):
    results = []
    information_requests = []
    prioritized_explanations = []

    for req in requirements:
        # Call the API-based flan-t5-xxl model to get prioritization details
        explanation = analyze_with_flan(req)

        # Retrieve user-provided factors with defaults if not specified
        factors = responses.get(req, {})
        importance = float(factors.get("importance", 3))
        complexity = float(factors.get("complexity", 3))
        urgency = float(factors.get("urgency", 3))
        clarification = factors.get("clarification", "")

        # Mock weighted score for demonstration purposes
        weighted_score = (importance + urgency - complexity) / 3

        # Append any clarification if provided
        if clarification:
            explanation += f"\nNote: Clarification provided - '{clarification}'"

        results.append({
            'requirement': req,
            'score': weighted_score,
            'explanation': explanation
        })

    # Sort requirements by weighted score in descending order
    prioritized_requirements = sorted(results, key=lambda x: x['score'], reverse=True)

    if len(prioritized_requirements) > 1:
        comparative_text = generate_comparative_text(prioritized_requirements)
        prioritized_explanations.append(comparative_text)

    return prioritized_requirements, information_requests, prioritized_explanations


def generate_explanation(req, importance, complexity, urgency, score):
    explanation = f"'{req}' has a score of {score:.2f} based on the following factors:\n"
    
    # Detailed explanation for importance
    explanation += f" - **Importance** rated at {importance}, which suggests "
    if importance > 4:
        explanation += "this requirement is crucial to the project's goals and should be addressed promptly. "
    elif 3 <= importance <= 4:
        explanation += "it aligns well with project objectives, making it moderately important. "
    else:
        explanation += "it has a lower impact on overall project objectives, suggesting it may be less critical. "
    
    # Detailed explanation for complexity
    explanation += f"\n - **Complexity** rated at {complexity}, indicating "
    if complexity > 3:
        explanation += "a significant level of effort and resources required for implementation. This may affect scheduling and prioritization. "
    elif 2 <= complexity <= 3:
        explanation += "a manageable level of complexity, suggesting that it requires moderate resources but is feasible within the current timeline. "
    else:
        explanation += "minimal complexity, meaning it would require fewer resources, which may boost its priority. "
    
    # Detailed explanation for urgency
    explanation += f"\n - **Urgency** rated at {urgency}, meaning "
    if urgency > 4:
        explanation += "this requirement demands immediate attention and is crucial for timely implementation. "
    elif 3 <= urgency <= 4:
        explanation += "this requirement should be addressed soon but may not need immediate focus. "
    else:
        explanation += "its implementation can be delayed, as it is less time-sensitive. "
    
    # Priority level based on score
    if score > 0.7:
        explanation += "\nOverall, this requirement is prioritized highly due to its strong alignment with project goals and needs."
    elif 0.5 <= score <= 0.7:
        explanation += "\nThis requirement has a moderate priority, balancing relevance, feasibility, and timeliness."
    else:
        explanation += "\nThis requirement has a lower priority and could be revisited based on further project developments."

    return explanation



def generate_comparative_text(prioritized_requirements):
    top_priority = prioritized_requirements[0]
    lower_priority = prioritized_requirements[-1]

    comparative_text = (
        f"Comparatively, '{top_priority['requirement']}' is prioritized over '{lower_priority['requirement']}' "
        f"due to its higher importance and urgency scores. Specifically, '{top_priority['requirement']}' "
        f"has an importance rating of {top_priority['score']:.2f}, indicating it aligns closely with core project goals. "
        f"Meanwhile, '{lower_priority['requirement']}' has a lower importance rating, suggesting it may be "
        f"less essential in the initial project stages or could be deferred.\n"
        
        f"The complexity of '{lower_priority['requirement']}' also plays a role in its lower priority. Higher complexity "
        f"indicates more effort and resources needed, which could affect the project timeline. This comparative analysis "
        f"highlights how importance, complexity, and urgency collectively influence prioritization, with higher-ranked items "
        f"having stronger alignment in these factors."
    )
    return comparative_text
