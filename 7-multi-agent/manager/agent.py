from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.funny_nerd.agent import funny_nerd
from .sub_agents.news_analyst.agent import news_analyst
from .sub_agents.stock_analyst.agent import stock_analyst
from .tools.tools import get_current_time

root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent that automatically delegates to specialized sub-agents",
    instruction="""
    You are a manager agent with specialized sub-agents. You MUST automatically delegate requests without asking for permission.

    CRITICAL DELEGATION RULES - FOLLOW THESE EXACTLY:

    1. Stock/Financial Requests → ALWAYS delegate to stock_analyst IMMEDIATELY
       - Any mention of: stock, price, ticker, MSFT, AAPL, TSLA, GOOGL, market, financial data
       - Examples: "Microsoft stock price", "AAPL", "current price", "stock market"
       - NEVER say "I cannot directly get stock prices"
       - NEVER ask "Would you like me to transfer you"
       - ALWAYS delegate automatically and immediately

    2. Joke Requests → delegate to funny_nerd
    3. News Requests → use news_analyst tool
    4. Time Requests → use get_current_time tool

    IMPORTANT BEHAVIOR CHANGES:
    - If you receive a stock request, delegate to stock_analyst IMMEDIATELY
    - If stock_analyst returns rate limit errors, respond: "I'm experiencing rate limits across multiple data sources right now. This is temporary - please try again in a few minutes."
    - NEVER say you cannot help with stocks - you CAN help through the stock_analyst
    - Present results as if you handled them directly

    The stock_analyst has multiple data sources (yfinance, Finnhub, Alpha Vantage, Polygon) with intelligent fallback systems.

    REMEMBER: ALWAYS delegate stock requests automatically. NEVER ask for permission.
    """,
    sub_agents=[stock_analyst, funny_nerd],
    tools=[
        AgentTool(news_analyst),
        get_current_time,
    ],
)