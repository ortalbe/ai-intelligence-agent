import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_RAW = "raw-documents"
KAFKA_TOPIC_PROCESSED = "processed-documents"
KAFKA_GROUP_ID = "intelligence-agent"

# --- Spark ---
SPARK_APP_NAME = "IntelligenceAgent"
SPARK_MASTER = "local[*]"

# --- Vector Store ---
CHROMA_PERSIST_DIR = "./data/vectorstore"
CHROMA_COLLECTION = "intelligence"

# --- Data Sources ---
NEWSAPI_QUERY = "artificial intelligence OR machine learning OR technology"
NEWSAPI_PAGE_SIZE = 20
ARXIV_QUERY = "artificial intelligence"
ARXIV_MAX_RESULTS = 10
HACKERNEWS_LIMIT = 20

# --- Text Processing ---
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 50      # overlap between chunks
