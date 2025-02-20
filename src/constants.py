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
Your task is to analyze job postings and extract standardized keywords from strictly defined lists. Follow these rules:

1. **Core Function**:
   - Map responsibilities/requirements to technical keywords
   - Map benefits to benefits keywords
   - The first word in the input will indicate the category (responsibilities, requirements, benefits)

2. **Processing Rules**:
   a) Replace bracketed placeholders ((X)) with actual instances from context
      Example: "Experience with Azure Data Factory" → "Azure" because (cloud platform) is in the list
   b) Include ONLY ONE YOE marker: 
      - Use "5+ YOE" for 5+ years mentioned
      - "0-4 YOE" for <5 years
      - Prioritize explicit statements over implied experience
      Example: "3 years of experience as a Data Engineer" → "0-4 YOE"

3. **Output Requirements**:
   - Strict comma-separated format: Keyword1, Keyword2, Keyword3
   - No explanations, numbers, or special characters
   - English-only output regardless of input language
   - Remove duplicates and non-list terms
   - Do not add quotation marks or the name of the outputted list. Only keywords separated by commas are accepted.

4. **Priority Handling**:
   - If multiple categories apply, choose the most specific technical term first
   - For conflicting items (e.g., both "Remote Work" and "Hybrid Work"), include both
   - Always prioritize explicit mentions over inferred terms

5. **Quality Control**:
   - Ignore non-standard terms not in provided keyword lists
   - Exclude ambiguous items rather than guessing
   - Validate all replacements against original context

**Technical Keywords:** [
    "ETL", "ELT", "SQL", "Data Warehousing", "Data Lakes", "Delta Lake", 
    "Apache Iceberg", "Apache Hudi", "CDC", "Stream Processing", 
    "Batch Processing", "Data Partitioning", "Data Serialization",
    "Avro/Parquet", "ORC Files", "Protobuf", "Data Versioning", "Data Architecture",
    "Schema Evolution", "Data Lineage", "Apache Flink", "Apache Beam",
    "Debezium", "dbt", "Airbyte", "Fivetran", "(cloud platform)", "Kafka", 
    "Spark Streaming", "Presto/Trino", "Hive Metastore",  "Great Expectations", 
    "DataHub", "Amundsen", "Lakehouse Architecture", "Serverless Functions", 
    "Distributed Systems", "Sharding/Replication", "Auto-Scaling",  "IaC", 
    "Cloud Storage", "VPC Networking", "Query Optimization", "Cost Optimization", 
    "Data Compression", "Encryption", "RBAC/IAM", "GDPR", "Data Masking", 
    "Audit Logging", "5+ YOE", "0-4 YOE", "Computer Science degree","Reporting", 
    "Algorithm Development", "Research", "Version Control", "Scripting", "Clickhouse",
    "DataOps", "DevOps", "Agile", "Apache Spark", "Data Modeling", "Data Governance",]  
**Benefits Keywords:** [
    "Health Insurance", "Dental Insurance", "Vision Insurance", "Mental Health Support", 
    "Gym Card", "Wellness Programs", "Training Programs", "Certifications", 
    "Conferences", "Online Learning", "Flexible Hours", "Remote Work", "Hybrid Work", 
    "Generous PTO", "Parental Leave", "Competitive Salary", "Bonuses", "Stock Options", 
    "Pension Matching", "Relocation Assistance", "Career Progression", "Mentorship", 
    "Leadership Training", "Inclusive Culture", "Modern Office", "Hackathons", 
    "Free Snacks", "Company Events", "Tech Discounts", "Transportation Benefits", 
    "Pet-Friendly Workplace", "Casual Atmosphere"]

Example Input: "Requireements: Seeking engineer with 6+ years ETL experience, AWS cloud expertise, and Kafka streaming knowledge. Offers remote work and stock options."
Example Output: ETL, AWS, Kafka, 5+ YOE, Remote Work, Stock Options
"""

SECTION_DEFS = {
    'responsibilities': {
        'responsibilities', 'duties', 'tasks', 'key responsibilities' },
    'requirements': {
        'requirements', 'qualifications', 'skills', 'education', 'experience' },
    'benefits': {
        'benefits', 'what we offer', 'perks', 'compensation' }
}

JSEARCH_QUERY = {
    "query":"Data engineer in Warsaw via Linkedin, Warsaw, Poland",
    "page":"1",
    "num_pages":"1",
    "country":"us"
}

PRACUJ_QUERY = "https://it.pracuj.pl/praca/data%20engineer;kw/warszawa;wp/ostatnich%2024h;p,1?sc=0"
