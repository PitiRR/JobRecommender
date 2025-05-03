from enum import Enum, auto


JOBLEVELS = {
    "junior": ["junior", "graduate"],
    "mid": ["mid", "regular"],
    "senior": ["senior", "lead"]
}

MODES = {
    "remote": ["remote", "remote work", "home office work", "zdalnie", "praca zdalna"],
    "hybrid": ["hybrid", "hybrid work", "praca hybrydowa"],
    "office": ["office", "full office work", "praca stacjonarna"],
    "mobile": ["mobile work", "praca mobilna"]
}

SCHEDULES = {
    "full-time": ["full-time", "pełny etat", "full time"],
    "part-time": ["part-time", "pół etatu", "part time"]
}

EMPLOYMENTS = {
    "permanent": ["umowa o pracę", "contract of employment"],
    "b2b": ["kontrakt b2b", "b2b contract"],
    "contract": ["umowa zlecenie", "umowa o dzieło", "contractor"]
}

class TimePeriod(Enum):
    HOURLY = auto()
    MONTHLY = auto()
    YEARLY = auto()

SYSTEM_MESSAGE = """
Extract predefined Technical or Benefits keywords from job posting text. The first word indicates the category (responsibilities, requirements, benefits) and determines which keyword list to use.

**Instructions:**

1.  **Keyword Mapping:**
    * Map responsibilities/requirements text -> **Technical Keywords**.
    * Map benefits text -> **Benefits Keywords**.
    * Replace placeholders like `(cloud platform)` with specific instances found in the text (e.g., "Azure Data Factory" maps to "Azure" if `(cloud platform)` is in the list).
    * Standardize experience: Use "5+ YOE" for 5+ years, "0-4 YOE" for <5 years. Prioritize explicit mentions.

2.  **Output Requirements:**
    * Format: Comma-separated keywords ONLY (e.g., `Keyword1,Keyword2`).
    * Content: Must be keywords strictly from the provided lists. English only. Deduplicated.
    * Exclusions: No quotes, explanations, numbers, non-list terms, or special characters.

3.  **Prioritization & Quality:**
    * Prioritize specific technical terms over general ones if multiple apply.
    * Include conflicting benefits if mentioned (e.g., both "Remote Work", "Hybrid Work").
    * Explicit mentions > inferred terms.
    * Ignore ambiguous terms or terms not in the lists. Validate placeholder replacements against context.
    * Input text may be in a different language. Output is always in English.

**Technical Keywords:** [
    ETL, ELT, SQL, Data Warehousing, Data Lakes, Lakehouse Architecture, Delta Lake, Apache Iceberg, 
    Apache Hudi, CDC (Change Data Capture), Stream Processing, Batch Processing, Apache Spark, 
    Spark Streaming, Apache Flink, Apache Beam, Kafka, Data Partitioning, Data Serialization, 
    Avro/Parquet, ORC Files, Protobuf, PostgreSQL, MySQL, MongoDB, NoSQL, Redis, Cassandra, Clickhouse, 
    Graph Databases, Presto/Trino, Hive Metastore, Query Optimization, Python, Java, Scala, Go, C++, C#, 
    JavaScript, TypeScript, Rust, Scripting, Object-Oriented Programming (OOP), Functional Programming,
    REST APIs, GraphQL, Microservices Architecture, Node.js, Django, Flask, Spring Boot, Ruby on Rails, 
    .NET Core, React, Angular, Vue.js, (cloud platform), AWS, Azure, GCP, Cloud Storage, Serverless Functions, 
    Distributed Systems, Sharding/Replication, Auto-Scaling, IaC (Infrastructure as Code), Terraform, 
    VPC Networking, Cost Optimization, Data Compression, Docker, Kubernetes, Data Modeling, Data Architecture, 
    Data Governance, Schema Evolution, Data Lineage, Data Versioning, Data Quality, Great Expectations, DataHub, 
    Amundsen, GDPR, Data Masking, Encryption, RBAC/IAM, Version Control, Git, CI/CD, Jenkins, GitLab CI, GitHub Actions, 
    CircleCI, DevOps, DataOps, Agile, System Design, Scalability, Performance Tuning, Testing, Unit Testing, 
    Integration Testing, E2E Testing, TDD, BDD, Observability, Monitoring, Logging, Tracing, Security Best Practices,
    5+ YOE, 0-4 YOE, Computer Science degree, Algorithm Development, Research, Reporting]
**Benefits Keywords:** [
    Competitive Salary, Bonuses, Stock Options, Retirement Plan, Health Insurance, Employee Assistance Program, 
    Gym Membership, Wellness Programs, Flexible Hours, Remote Work, Hybrid Work, Generous PTO (Paid Time Off), 
    Parental Leave, Training Programs, Certifications, Career Progression, Mentorship, Leadership Training,
    Inclusive Culture, Modern Office, Casual Atmosphere, Hackathons, Free Snacks / Catered Meals, Company Events, 
    Tech Discounts, Commuter Benefits, Relocation Assistance]

**Example Input:** "Requireements: Seeking engineer with 6+ years ETL experience, AWS cloud expertise, and Kafka streaming knowledge. Offers remote work and stock options."
**Example Output:** ETL, AWS, Kafka, 5+ YOE, Remote Work, Stock Options
"""

SECTION_DEFS = {
    'responsibilities': {
        'responsibilities', 'duties', 'tasks', 'key responsibilities', 'as a', 'you will','role',},
    'requirements': {
        'requirements', 'qualifications', 'skills', 'education', 'experience,' 'we are looking for', 'poszukujemy'},
    'benefits': {
        'benefits', 'what we offer', 'perks', 'compensation', 'offers', 'oferujemy', 'benefity'}
}

JSEARCH_QUERY = {
    "query":"Data engineer in Warsaw via Linkedin, Warsaw, Poland",
    "page":"1",
    "num_pages":"1",
    "country":"us"
}

PRACUJ_QUERY = "https://it.pracuj.pl/praca/data%20engineer;kw/warszawa;wp/ostatnich%2024h;p,1?sc=0"
