import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# Output schema
class HarvestingCost(BaseModel):
    estimated_cost: str = Field(description="Estimated cost range (INR) for constructing the harvesting system")
    govt_schemes: str = Field(description="Government schemes available in the user's location (or 'No schemes available')")

parser = PydanticOutputParser(pydantic_object=HarvestingCost)

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert in rainwater harvesting cost estimation and policy schemes."),
    ("user", """Given the following user details:
    Harvesting type: {harvesting_type}
    Location: {location}

    Provide:
    1. An estimated cost range (INR) for implementing this harvesting system.
    2. Any government schemes available in that location.

    Return the output in JSON format as per the given schema.
    {format_instructions}""")
])

final_prompt = prompt.partial(format_instructions=parser.get_format_instructions())


def _build_chain():
    """Create the Gemini chain after confirming its API key is configured."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to the environment or a .env file."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=api_key,
        temperature=0,
    )
    return final_prompt | llm | parser

# Main function
def analyze_cost_and_schemes(harvesting_type: str, location: str):
    """Estimate harvesting costs and identify schemes for a location.

    Scheme suggestions come from the language model and should be verified
    against current official sources before a user relies on them.
    """
    chain = _build_chain()
    result = chain.invoke({
        "harvesting_type": harvesting_type,
        "location": location
    })
    # Pydantic v2 uses model_dump(); dict() keeps compatibility with v1.
    if hasattr(result, "model_dump"):
        return result.model_dump()
    return result.dict()
