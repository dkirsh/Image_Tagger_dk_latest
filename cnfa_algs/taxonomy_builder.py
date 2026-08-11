"""
Taxonomy Builder (Wave 3 Semantic Pipeline - Engine 1)

This module implements the "Self-Increasing Taxonomy" by running a VLM over images.
It anchors the VLM's freedom to the Canonical Dictionary (Neufert & Alexander).
Discoveries are mapped to equivalence classes first; novel appendages and items 
are added as second-order dynamic classifications.
"""

import json
import yaml
import os
from typing import List, Dict, Any

CANONICAL_ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "neufert_alexander_ontology.yaml")
DYNAMIC_REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "dynamic_architectural_taxonomy.json")

# ---------------------------------------------------------------------------
# Core VLM Prompt (Enforcing Equivalence Classes)
# ---------------------------------------------------------------------------
TAXONOMY_DISCOVERY_PROMPT = """
You are an expert architectural surveyor adhering to Neufert's "Architects' Data" and Christopher Alexander's "A Pattern Language".
Your task is to identify every distinct architectural feature, partition, fixture, and piece of furniture in the provided image.

CRITICAL DIRECTIVE - EQUIVALENCE CLASSES:
You must FIRST attempt to map every item you find to the provided CANONICAL DICTIONARY.
If (and only if) an item fundamentally does not fit any canonical class (e.g., a bizarre distortion, a novel type of half-height cubicle, or a unique appendage), you may invent a highly precise, descriptive "second-order" term for it.

Output your findings as a strict JSON list of objects, where each object has:
{
  "detected_item": "description of what you see",
  "mapped_canonical_id": "the ID from the dictionary, or null if it's completely novel",
  "novel_classification": "your invented term (only if mapped_canonical_id is null, otherwise null)",
  "confidence": 0.0 to 1.0
}
"""

class TaxonomyBuilder:
    def __init__(self, use_mock_vlm: bool = False):
        self.use_mock_vlm = use_mock_vlm
        self.canonical_ontology = self._load_canonical()
        self.dynamic_registry = self._load_dynamic_registry()

    def _load_canonical(self) -> Dict[str, Any]:
        if not os.path.exists(CANONICAL_ONTOLOGY_PATH):
            return {}
        with open(CANONICAL_ONTOLOGY_PATH, 'r') as f:
            return yaml.safe_load(f)

    def _load_dynamic_registry(self) -> List[Dict[str, Any]]:
        if not os.path.exists(DYNAMIC_REGISTRY_PATH):
            return []
        with open(DYNAMIC_REGISTRY_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def _save_dynamic_registry(self):
        with open(DYNAMIC_REGISTRY_PATH, 'w') as f:
            json.dump(self.dynamic_registry, f, indent=2)

    def scan_image(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Scans an image using the VLM, maps to equivalence classes, and expands the dynamic registry.
        """
        print(f"Scanning image: {image_path}")
        
        # Prepare the prompt payload with the canonical dictionary embedded
        prompt_payload = TAXONOMY_DISCOVERY_PROMPT + "\n\nCANONICAL DICTIONARY:\n" + yaml.dump(self.canonical_ontology)
        
        # Call the VLM (Mocked for integration/testing phase; would route to Gemini/GPT-4o)
        vlm_results = self._call_vlm(image_path, prompt_payload)
        
        new_discoveries = []
        for item in vlm_results:
            if item.get("mapped_canonical_id") is None and item.get("novel_classification"):
                # This is a novel, second-order discovery!
                novel_term = item["novel_classification"]
                # Check if we already registered it
                if not any(entry["id"] == novel_term for entry in self.dynamic_registry):
                    print(f"[*] Discovered NOVEL architectural feature: {novel_term}")
                    new_entry = {
                        "id": novel_term,
                        "source": "VLM_Dynamic_Discovery",
                        "description": item.get("detected_item"),
                        "first_seen_in": os.path.basename(image_path)
                    }
                    self.dynamic_registry.append(new_entry)
                    new_discoveries.append(new_entry)

        if new_discoveries:
            self._save_dynamic_registry()
            
        return vlm_results

    def _call_vlm(self, image_path: str, prompt: str) -> List[Dict[str, Any]]:
        """
        Stub for VLM API call (e.g. Gemini 1.5 Pro).
        Returns a structured JSON response of recognized parts.
        """
        if self.use_mock_vlm:
            # Mock response for testing the equivalence classes logic
            return [
                {
                    "detected_item": "Standard hinged wooden door",
                    "mapped_canonical_id": "door.standard_swing",
                    "novel_classification": None,
                    "confidence": 0.95
                },
                {
                    "detected_item": "A bizarre floating metallic appendage hanging from the ceiling",
                    "mapped_canonical_id": None,
                    "novel_classification": "fixture.ceiling_suspended_metallic_appendage",
                    "confidence": 0.88
                },
                {
                    "detected_item": "Low partition wall separating desks",
                    "mapped_canonical_id": "wall.half_height_partition",
                    "novel_classification": None,
                    "confidence": 0.92
                }
            ]
        else:
            raise NotImplementedError("Production VLM integration (Gemini/OpenAI) goes here.")

if __name__ == "__main__":
    builder = TaxonomyBuilder(use_mock_vlm=True)
    results = builder.scan_image("/dummy/path/to/target_office_01.jpg")
    print("VLM Output:", json.dumps(results, indent=2))
    print("Updated Dynamic Registry Size:", len(builder.dynamic_registry))
