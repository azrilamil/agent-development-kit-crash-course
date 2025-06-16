# Configuration for Stock Analyst Agent

# Cache settings
CACHE_DURATION_MINUTES = 5  # How long to cache stock prices
MAX_CACHE_SIZE = 100  # Maximum number of stocks to cache

# Retry settings
MAX_RETRIES = 3  # Maximum number of retry attempts
BASE_RETRY_DELAY = 1  # Base delay in seconds for exponential backoff
MAX_RETRY_DELAY = 30  # Maximum delay between retries

# Request settings
REQUEST_TIMEOUT = 10  # Timeout for API requests in seconds
RATE_LIMIT_DELAY = 60  # How long to wait when rate limited (seconds)

# Alternative API settings (configure these if you want to use alternative sources)
ALPHA_VANTAGE_API_KEY = "1ZXKV7AULGLUBWTW"  # Set to your Alpha Vantage API key
FINNHUB_API_KEY = "d17c889r01qtc1t7fecgd17c889r01qtc1t7fed0"  # Set to your Finnhub API key
POLYGON_API_KEY = "2pPcQNurNHbFwHU9ngXHbhxWN_ezAKFr"  # Set to your Polygon.io API key

# Debug settings
DEBUG_MODE = True  # Set to False to reduce console output
LOG_CACHE_HITS = True  # Whether to log when cache is used