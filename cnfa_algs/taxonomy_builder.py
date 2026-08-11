import json
import yaml
import os
import pydantic
import asyncio
from typing import List, Optional
from google.antigravity import Agent, LocalAgentConfig
from google.antigravity.types import Image

CANONICAL_ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "neufert_alexander_ontology.yaml")
DYNAMIC_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "dynamic_architectural_taxonomy.json")

class DetectedElement(pydantic.BaseModel):
    detected_item: str
    mapped_canonical_id: Optional[str]
    novel_classification: Optional[str]
    confidence: float

class ImageAnalysis(pydantic.BaseModel):
    elements: List[DetectedElement]

class TaxonomyBuilder:
    def __init__(self):
        self.canonical_ontology = self._load_canonical()
        self.dynamic_registry = self._load_dynamic_registry()
        
    def _load_canonical(self):
        if not os.path.exists(CANONICAL_ONTOLOGY_PATH):
            return {}
        with open(CANONICAL_ONTOLOGY_PATH, 'r') as f:
            return yaml.safe_load(f)

    def _load_dynamic_registry(self):
        if not os.path.exists(DYNAMIC_REGISTRY_PATH):
            return []
        with open(DYNAMIC_REGISTRY_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _save_dynamic_registry(self):
        with open(DYNAMIC_REGISTRY_PATH, 'w') as f:
            json.dump(self.dynamic_registry, f, indent=4)

    async def scan_image_async(self, image_path: str):
        print(f"Scanning image: {image_path}")
        
        # Build prompt incorporating the canonical ontology
        prompt = f"""
        Analyze this image and identify all architectural and spatial elements.
        Map them to the following canonical IDs if they fit perfectly.
        If they do not fit, propose a novel classification string (dot-separated) and set mapped_canonical_id to null.
        
        Canonical Ontology:
        {json.dumps(self.canonical_ontology.get('architectural_elements', {}), indent=2)}
        """

        config = LocalAgentConfig(
            response_schema=ImageAnalysis,
            system_instructions="You are an expert architectural VLM. Extract elements with high precision."
        )

        try:
            image = Image.from_file(image_path)
            async with Agent(config) as agent:
                response = await agent.chat([prompt, image])
                data = await response.structured_output()
                
                if data and "elements" in data:
                    print(f"VLM Output:\n{json.dumps(data['elements'], indent=2)}")
                    for elem in data["elements"]:
                        if elem.get("novel_classification"):
                            novel_id = elem["novel_classification"]
                            print(f"[*] Discovered NOVEL architectural feature: {novel_id}")
                            
                            # Add to registry if not already present
                            if not any(entry.get("id") == novel_id for entry in self.dynamic_registry):
                                self.dynamic_registry.append({
                                    "id": novel_id,
                                    "source": "vlm_discovery",
                                    "confidence_threshold": elem.get("confidence", 0.8)
                                })
                    self._save_dynamic_registry()
                    print(f"Updated Dynamic Registry Size: {len(self.dynamic_registry)}")
                else:
                    print("Error: VLM did not return a valid structured output.")
        except Exception as e:
            print(f"Error scanning image: {e}")

    def scan_image(self, image_path: str):
        """Synchronous wrapper for external callers"""
        asyncio.run(self.scan_image_async(image_path))

if __name__ == "__main__":
    builder = TaxonomyBuilder()
    # Dummy mock path to test the syntax without hitting the model on a missing file
    if os.path.exists("/dummy/path/to/target_office_01.jpg"):
        builder.scan_image("/dummy/path/to/target_office_01.jpg")
    else:
        print("TaxonomyBuilder initialized successfully. Ready to process real images.")
