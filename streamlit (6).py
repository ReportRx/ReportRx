!pip install pdf2image pillow openai

!pip install --upgrade openai==1.55.3 httpx==0.27.2

!pip install --upgrade openai httpx

!pip show openai

!pip install streamlit

!apt-get install poppler-utils

# !pip install pyngrok

"""**IMPORT**"""

import openai
import os
from pdf2image import convert_from_path
from PIL import Image
import base64
from openai import OpenAI

"""**API KEY**"""

os.environ["OPENAI_API_KEY"] = "xxxx"


client = OpenAI()

"""**PDF TO IMAGES**"""

def pdf_to_images(pdf_path, output_folder="output_images", dpi=300):
    """
    Converts a PDF into images, saving each page as a separate image.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i + 1}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)

    return image_paths

"""**COMBINE IMAGES**"""

def combine_images_vertically(image_paths, output_file="composite.png"):
    """
    Combines multiple images vertically into a single composite image.
    """
    images = [Image.open(image) for image in image_paths]
    combined_width = max(image.width for image in images)
    combined_height = sum(image.height for image in images)

    composite_image = Image.new("RGB", (combined_width, combined_height))
    y_offset = 0
    for image in images:
        composite_image.paste(image, (0, y_offset))
        y_offset += image.height

    composite_image.save(output_file)
    print(f"Composite image saved as {output_file}")
    return output_file

"""ENCODING TO BASE64 TO RESOLVE UTF-8 ISSUES"""

def encode_image_to_base64(image_path):
    """
    Encodes an image file to a Base64 string.
    """
    with open(image_path, "rb") as image_file:
        return f"data:image/png;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"

"""## ***PROMPT***"""

def analyze_composite_image(image_path):
    """
    Sends the composite image to OpenAI GPT-4 API for analysis.
    """
    base64_image = encode_image_to_base64(image_path)

    prompt = """
     Greetings, GPT! You are going to facilitate the Report Rx tech, an innovative medical report analyzer which has its approach implemented by a dynamic consortium of virtual experts, each serving a distinct role.

      Your role will be the Medical Expert (ME), a professional who has all knowledge with respect to the healthcare.. As the ME, you will facilitate the report rx process by following these key stages:

      1.Reading the images. Thoroughly read the report provided in the images and analyze every element in mentioned in the test.

      2.Generate the following output which will have different sections and each section will have a particular heading inside which there might me sub heading or pointers if needed.

      3. SECTIONS/HEADINGS are as follows-

      a) HEALTH SUMMARY

      Summarize the report findings by:

      Highlighting key observations (e.g., normal and abnormal values).

      Mentioning overall health implications (e.g., "Overall health is satisfactory, but some parameters indicate potential liver dysfunction and risk of anemia").

      Include a general assessment of whether the report suggests any immediate health concerns.

      Only mention levels of those parameters in this which seem abnormal. Also instead of this section being the final output it should be the intial summary which comforts the user/patient


      Example:
      "Overall, the report indicates satisfactory health. Blood sugar levels and kidney functions are within normal ranges. However, hemoglobin levels (11.2 g/dL, below the reference range of 12-15 g/dL) suggest mild anemia, and SGPT levels (56 IU/L, above the reference range of 7-40 IU/L) point to potential liver stress."

      b) Glance at Important Parameters
      List critical health parameters, organizing them by category (e.g., Glucose, Liver Function, Lipid Profile, etc.), and flag those that are abnormal or near-boundary values.

      Example:

      Glucose:

      Fasting Glucose: 89 mg/dL (Normal)

      HbA1c: 5.6% (Normal, but approaching pre-diabetes threshold)


      Liver Function:

      SGPT (ALT): 56 IU/L (High, above 7-40 IU/L)

      SGOT (AST): 42 IU/L (Slightly High, above 10-40 IU/L)


      Blood Count:

      Hemoglobin: 11.2 g/dL (Low, reference range: 12-15 g/dL)


      Lipid Profile:

      Total Cholesterol: 230 mg/dL (High, above 200 mg/dL)

      Under each test , this should cover all the paramters and if any parameter is abornal it should be mentioned in bold.

      c) POTENTIAL RISKS

      This should start with lines like (" since ur report has abnormalities such as mention the abnormals with range ( verbose 1)

      Followed by this it should mention thr risks such as if glucose is high then maybe diabetes or if lymphocyte count is high then it may point to any infection somewhere in the body. ( Verbose-2)

      After this there should be a nested sub-heading - " WHY ARE U PRONE TO THESE DISEASES "
      This subheading should be detailed and should contain the following info -

      For each flagged/abmnormal parameter, provide:

      Explanation of the Parameter: Explain the role of the parameter in health (e.g., "Hemoglobin is essential for oxygen transport in the blood").

      Observed Value and Reference Range: Clearly state the observed value and the normal range.

      Health Implications: Explain what deviations mean (e.g., "Low hemoglobin may indicate anemia, possibly due to iron deficiency").

      Actions not performed - mention all those actions performed by the patient  / lifestyle that might be carried by the patient / intakes that the patient is missing due to which the above parameter is abnoraml



      Example:

      Hemoglobin (11.2 g/dL, Low):

      Explanation: Hemoglobin is a protein in red blood cells that carries oxygen to the body.

      Implications: Low levels suggest anemia, which could result in fatigue, weakness, or more serious complications if untreated.

      Unintended actions - iron deficient diet , less exercise etc


      SGPT (ALT, 56 IU/L, High):

      Explanation: SGPT is a liver enzyme that indicates liver health. Elevated levels often signify liver stress or damage.

      Implications: This may be caused by fatty liver, alcohol consumption, or medications.

      Unintended actions - " "

      d)Diet Do's and Don'ts:
      Provide dietary recommendations based on abnormal parameters. Categorize them into foods to include and avoid, targeting the specific issues flagged.

      Example:

      For Anemia:

      Foods to Include: Spinach, lentils, tofu, red meat, dates, vitamin C-rich foods like oranges (to enhance iron absorption).

      Foods to Avoid: Tea and coffee near meals (reduce iron absorption).


      For High Cholesterol:

      Foods to Include: Oats, flaxseeds, nuts (almonds, walnuts), fatty fish (salmon, mackerel), olive oil.

      Foods to Avoid: Fried foods, processed meats, butter, and cheese.


      e)5. Consolidated Guidance:
      Provide a summary of recommendations for overall health improvement, considering the combined impact of the report findings. Include:

      Medical follow-up advice (e.g., "Consult a gastroenterologist for liver enzyme abnormalities").

      This should convince the user that although there is nothing to worry about and should consult a specialist if possible to ensure safety.

      f) FINAL SUMMARY


      Just a detailed summary of everything that has been mentioned above that seems satisfactory to the user/patient.


    """

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a medical expert analyzing the provided image."},
            {"role": "user", "content": [{"type": "text", "text": prompt},
                                         {"type": "image_url", "image_url": {"url": base64_image}}]},
        ],
        temperature=0.7
    )
    return response.choices[0].message.content



"""**RESULT**"""

if __name__ == "__main__":
    # Path to your PDF in Google Colab
    pdf_path = "/content/36305b60af9b35f2b7b415d388b19e4a.pdf"  # Update with your PDF file path

    # Convert PDF to images
    output_folder = "/content/output_images"
    image_paths = pdf_to_images(pdf_path, output_folder=output_folder)

    #Combine images vertically into a composite image
    composite_image_path = "/content/composite.png"
    composite_image_path = combine_images_vertically(image_paths, composite_image_path)

    #Analyze the composite image
    if composite_image_path:
        print("Analyzing the composite image...")
        analysis_result = analyze_composite_image(composite_image_path)
        print("\nAnalysis Result:")
        print(analysis_result)

"""STREAMLIT SETUP ( IGNORE )"""

import streamlit as st

# # Streamlit App
# st.title("📄 Report Rx Analyzer")

# st.sidebar.header("Upload and Analyze Medical Reports")
# uploaded_file = st.sidebar.file_uploader("Upload a PDF File", type="pdf")

# # Tabs for Sections
# if uploaded_file:
#     st.sidebar.success("File Uploaded Successfully!")
#     with st.spinner("Processing your report..."):
#         # Convert PDF to images
#         image_paths = pdf_to_images(uploaded_file.name, output_folder="temp_images")
#         composite_image_path = combine_images_vertically(image_paths, output_file="composite_temp.png")
#         analysis_result = analyze_composite_image(composite_image_path)

#     tabs = st.tabs(["Health Summary", "Important Parameters", "Potential Risks", "Diet Do's and Don'ts", "Consolidated Guidance", "Final Summary"])

#     # Example of rendering sections dynamically
#     with tabs[0]:
#         st.header("Health Summary")
#         st.write("Summarized insights from the medical report:")
#         st.success(analysis_result.get("health_summary", "No summary available."))

#     with tabs[1]:
#         st.header("Important Parameters")
#         st.write("Critical health parameters from the report:")
#         st.warning(analysis_result.get("important_parameters", "No details available."))

#     with tabs[2]:
#         st.header("Potential Risks")
#         st.write("Risks associated with the report findings:")
#         st.error(analysis_result.get("potential_risks", "No risks identified."))

#     with tabs[3]:
#         st.header("Diet Do's and Don'ts")
#         st.write("Dietary recommendations based on the report:")
#         st.info(analysis_result.get("diet_recommendations", "No recommendations available."))

#     with tabs[4]:
#         st.header("Consolidated Guidance")
#         st.write("Overall health improvement suggestions:")
#         st.success(analysis_result.get("consolidated_guidance", "No guidance available."))

#     with tabs[5]:
#         st.header("Final Summary")
#         st.write("Comprehensive summary of all findings:")
#         st.info(analysis_result.get("final_summary", "No summary available."))

#     st.sidebar.image(composite_image_path, caption="Processed Composite Image", use_column_width=True)
