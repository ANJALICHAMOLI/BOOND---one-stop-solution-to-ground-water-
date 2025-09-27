# app/agents/harvesting_agent.py
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Load .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it in your .env file.")

# Output schema
class HarvestingDecision(BaseModel):
    can_build: bool = Field(description="Whether rooftop harvesting is feasible or not")
    harvesting_type: str = Field(description="Recommended type of rooftop rainwater harvesting (if feasible)")
    reason: str = Field(description="Reasoning behind the decision")

parser = PydanticOutputParser(pydantic_object=HarvestingDecision)

# Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,  # ✅ explicitly passed
    temperature=0
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in rainwater harvesting feasibility analysis."),
    ("user", """Given the user details:
    Location: {location}
    Roof area: {roof_area} sq. meters
    Open space: {open_space} sq. meters

    Decide whether rooftop rainwater harvesting can be implemented.
    {format_instructions}""")
])

final_prompt = prompt.partial(format_instructions=parser.get_format_instructions())
chain = final_prompt | llm | parser

# Main function to call
def analyze_feasibility(location: str, roof_area: float, open_space: float):
    result = chain.invoke({
        "location": location,
        "roof_area": roof_area,
        "open_space": open_space
    })
    return result.dict()
