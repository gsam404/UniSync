# University-wide topics
UNIVERSITY_TOPICS = {
    "university.announcements",
    "university.academic",
    "university.events",
    "university.emergency",
    "university.it",
    "university.library",
}

# College-specific topics
COLLEGE_TOPICS = {
    "college.ict",
    "college.business",
    "college.engineering",
    "college.education",
    "college.arts_sciences",
    "college.nursing",
    "college.agriculture",
}

# Combine all valid topics
VALID_TOPICS = UNIVERSITY_TOPICS | COLLEGE_TOPICS


def is_valid_topic(topic):
    """
    Checks whether a topic is recognized by UniSync.
    """
    return isinstance(topic, str) and topic in VALID_TOPICS