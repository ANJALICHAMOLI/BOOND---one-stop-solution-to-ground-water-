import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Output schema
class HarvestingDecision(BaseModel):
    can_build: bool = Field(description="Whether rooftop harvesting is feasible or not")
    harvesting_type: str = Field(description="Recommended type of rooftop rainwater harvesting (if feasible)")
    reason: str = Field(description="Reasoning behind the decision")

parser = PydanticOutputParser(pydantic_object=HarvestingDecision)

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


def _build_chain():
    """Load credentials and create the Gemini chain when it is needed."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the environment or a .env file."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        api_key=api_key,
    )
    return final_prompt | llm | parser

# Main function to call
def analyze_feasibility(location: str, roof_area: float, open_space: float):
    """Assess harvesting feasibility using the provided location and areas."""
    if roof_area <= 0:
        raise ValueError("roof_area must be greater than 0 square meters.")
    if open_space < 0:
        raise ValueError("open_space cannot be negative.")

    chain = _build_chain()
    result = chain.invoke({
        "location": location,
        "roof_area": roof_area,
        "open_space": open_space
    })
    # Pydantic v2 uses model_dump(); dict() keeps compatibility with v1.
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result.dict()
