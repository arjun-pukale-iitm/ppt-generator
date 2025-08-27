from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io, json, re
from pptx_utils import inspect_template_bytes, build_presentation_from_plan
from llm_clients import call_llm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Allow frontend requests from any domain (or restrict to specific ones)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify ["http://localhost:5500", "https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def hello():
    return "hello, go to /static"

@app.post("/api/generate")
async def generate_pptx(
    text: str = Form(...),
    guidance: str = Form(""),
    provider: str = Form("openrouter"),
    api_key: str = Form(...),
    template: UploadFile = File(...)
):
    """
    Generate a PPTX from provided text using a chosen LLM provider and PPTX/POTX template.
    """

    # --- Step 1: Read template bytes
    template_bytes = await template.read()

    # --- Step 2: Inspect template -> inventory
    inventory = inspect_template_bytes(io.BytesIO(template_bytes))

    # --- Step 3: Build improved prompt
    prompt = f"""
You are to create a structured slide plan from the given text.

Inventory of available layouts and images (do not include this in the output):
{json.dumps(inventory, indent=2)}

Guidance: {guidance}

Text to convert into slides:
{text}

Output:
- STRICTLY return valid JSON.
- No comments, explanations, or text outside JSON.
- Schema:
{{
  "slides": [
    {{
      "title": "string - title of the slide",
      "layout_index": 0,
      "bullets": ["string", "string"],
      "notes": "string - speaker notes, optional",
      "image_from_template_hint": "string or empty"
    }}
  ],
  "metadata": {{
    "total_slides": int,
    "generated_by": "{provider}",
    "guidance_used": "{guidance}"
  }}
}}
"""

    # --- Step 4: Call correct LLM provider
    try:
        llm_response = await call_llm(provider, api_key, prompt)
        print("Raw LLM response:", llm_response[:500])  # Debug log (truncated)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {str(e)}")

    # --- Step 5: Parse JSON safely (with auto-repair)
    try:
        plan = json.loads(llm_response)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\})", llm_response, re.S)
        if not match:
            raise HTTPException(status_code=500, detail="LLM did not return valid JSON.")
        try:
            plan = json.loads(match.group(1))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse JSON even after cleanup: {str(e)}")

    # --- Step 6: Build PPTX from template + plan
    try:
        out_bytes = build_presentation_from_plan(io.BytesIO(template_bytes), plan)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build PPTX: {str(e)}")

    # --- Step 7: Return generated PPTX as download
    return StreamingResponse(
        out_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=generated.pptx"}
    )
