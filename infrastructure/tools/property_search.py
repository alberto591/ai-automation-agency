from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from domain.ports import DatabasePort


class PropertySearchInput(BaseModel):
    query: str = Field(description="Search query for properties (e.g. '3 bedrooms in Florence')")
    budget: int = Field(default=0, description="Max budget in Euros")


class PropertySearchTool(BaseTool):
    name: str = "property_search"
    description: str = (
        "Search for real estate properties in the agency database. "
        "Use this when a user asks about available listings."
    )
    args_schema: type[BaseModel] = PropertySearchInput
    db: DatabasePort

    def _run(self, query: str, budget: int = 0) -> str:
        try:
            # Basic search implementation using the port
            properties = self.db.get_properties(query=query, limit=3)

            if not properties:
                return "No specific properties found matching the criteria."

            result = "Found the following properties:\n"
            for p in properties:
                price = f"€{p.get('price', 0):,}"
                title = p.get("title", "Unknown Property")
                result += f"- {title}: {price}\n"

            return result
        except Exception as e:
            return f"Error searching properties: {str(e)}"
