# # gemini_video_evaluator.py
# # A script to evaluate Gemini 1.5 Pro's Q&A capabilities on a specific YouTube video segment.

# import os
# import sys
# import logging
# import json
# import pandas as pd
# from dotenv import load_dotenv

# import google.generativeai as genai
# from google.generativeai.types import HarmCategory, HarmBlockThreshold

# from thefuzz import fuzz
# from openpyxl.chart import BarChart, Reference

# # --- SCRIPT CONFIGURATION ---
# # --- Please edit all variables in this section before running ---

# # 1. API and Model Configuration
# # Load the API key from the .env file
# load_dotenv()
# API_KEY = os.getenv("GOOGLE_API_KEY")
# # The latest Gemini 1.5 Pro model is recommended for its video understanding capabilities
# MODEL_NAME = "gemini-1.5-pro-latest"

# # 2. Video and Segment Configuration
# YOUTUBE_URL = "https://www.youtube.com/watch?v=668nUCeBHyY" # Example: A video about the James Webb Space Telescope
# START_TIME = "00:01:05" # Format: "HH:MM:SS"
# END_TIME = "00:02:10"   # Format: "HH:MM:SS"

# # 3. Questions and Answers Configuration
# # Ensure the number of items in QUESTIONS, REFERENCE_ANSWERS, and QUESTION_IDS are the same.
# QUESTIONS = [
#     "What is the primary subject being shown and discussed in this segment?",
#     "What specific capability of the telescope is mentioned?",
#     "What celestial object is shown as an example of the telescope's capability?"
# ]
# REFERENCE_ANSWERS = [
#     "The James Webb Space Telescope's ability to see in infrared light.",
#     "It can see the first stars and galaxies that formed in the early universe.",
#     "The 'Pillars of Creation'."
# ]
# QUESTION_IDS = ["Q01-Subject", "Q02-Capability", "Q03-Example"]

# # 4. Evaluation and Output Configuration
# # A similarity score (0-100) to consider an answer correct.
# # fuzz.token_sort_ratio is good for matching answers where word order might differ.
# SIMILARITY_THRESHOLD = 75
# OUTPUT_FILENAME = "Gemini_Video_QA_Evaluation_Results.xlsx"

# # --- END OF CONFIGURATION ---


# # --- Logging Setup ---
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')


# def setup_gemini():
#     """Configures the Gemini API key and safety settings."""
#     if not API_KEY:
#         logging.error("Google API Key not found. Please check your .env file.")
#         sys.exit(1)
#     try:
#         genai.configure(api_key=API_KEY)
#         logging.info("Gemini API configured successfully.")
#     except Exception as e:
#         logging.error(f"Failed to configure Gemini API: {e}")
#         sys.exit(1)

# def compare_answers(gemini_answer: str, reference_answer: str) -> tuple[bool, int]:
#     """
#     Compares two strings using fuzzy matching and returns correctness and score.
#     Returns: A tuple (is_correct, similarity_score)
#     """
#     # token_sort_ratio ignores word order, which is robust for LLM answers.
#     score = fuzz.token_sort_ratio(gemini_answer.lower(), reference_answer.lower())
#     is_correct = score >= SIMILARITY_THRESHOLD
#     return is_correct, score

# def create_accuracy_chart(excel_writer, data_sheet_name: str, total_questions: int):
#     """
#     (Bonus) Creates a bar chart summarizing accuracy in the Excel file.
#     """
#     logging.info("Creating accuracy summary chart in Excel file...")
#     try:
#         workbook = excel_writer.book
#         worksheet = excel_writer.sheets[data_sheet_name]

#         # Create a new sheet for the chart
#         chart_sheet = workbook.create_sheet(title="Accuracy Summary")

#         # Get the data for the chart
#         correct_count = worksheet['E'][1:].count('Correct')
#         incorrect_count = total_questions - correct_count

#         # Write summary data to the chart sheet
#         summary_data = [
#             ['Category', 'Count'],
#             ['Correct', correct_count],
#             ['Incorrect', incorrect_count]
#         ]
#         for row in summary_data:
#             chart_sheet.append(row)

#         # Create the bar chart
#         chart = BarChart()
#         chart.title = "Answer Accuracy"
#         chart.y_axis.title = "Number of Questions"
#         chart.x_axis.title = "Result"
        
#         data = Reference(chart_sheet, min_col=2, min_row=1, max_row=3, max_col=2)
#         categories = Reference(chart_sheet, min_col=1, min_row=2, max_row=3)
#         chart.add_data(data, titles_from_data=True)
#         chart.set_categories(categories)
#         chart.legend = None

#         chart_sheet.add_chart(chart, "E2")
#         logging.info("Chart created successfully.")
#     except Exception as e:
#         logging.error(f"Could not create the accuracy chart. Error: {e}")


# def main():
#     """Main function to orchestrate the video Q&A evaluation."""
#     setup_gemini()

#     # --- Input Validation ---
#     if not (len(QUESTIONS) == len(REFERENCE_ANSWERS) == len(QUESTION_IDS)):
#         logging.error("Input arrays (QUESTIONS, REFERENCE_ANSWERS, QUESTION_IDS) must have the same number of elements.")
#         sys.exit(1)

#     # --- Prompt Engineering for a Single, Optimized Request ---
#     # We will ask all questions at once and request a structured JSON response.
#     question_list_str = "\n".join([f"{i+1}. {q}" for i, q in enumerate(QUESTIONS)])

#     prompt = f"""
#     Please act as a video analysis expert. Analyze the video found at the provided YouTube URL,
#     focusing ONLY on the content between {START_TIME} and {END_TIME}.

#     Based exclusively on that specific video segment, provide concise answers to the following numbered questions.

#     Your response MUST be a valid JSON object. The keys of the JSON object should be the question numbers as strings (e.g., "1", "2", "3"),
#     and the values should be your string answers to the corresponding questions.

#     Questions:
#     {question_list_str}
#     """

#     logging.info(f"Analyzing video segment from {YOUTUBE_URL} ({START_TIME}-{END_TIME})...")
#     logging.info(f"Sending {len(QUESTIONS)} questions to Gemini in a single request.")

#     # --- API Call ---
#     try:
#         model = genai.GenerativeModel(MODEL_NAME)
#         video_part = genai.Part.from_uri(
#             uri=YOUTUBE_URL,
#             mime_type="video/mp4"
#         )
        
#         # Configure model to output JSON
#         generation_config = genai.GenerationConfig(response_mime_type="application/json")

#         response = model.generate_content(
#             [prompt, video_part],
#             generation_config=generation_config,
#             # Safety settings can be adjusted if default blocking is too aggressive
#             safety_settings={
#                 HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
#                 HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
#             }
#         )
        
#         # The API returns a JSON string, which we parse into a Python dictionary.
#         gemini_answers_dict = json.loads(response.text)
#         logging.info("Successfully received and parsed structured response from Gemini.")

#     except Exception as e:
#         logging.error(f"An error occurred during the Gemini API call: {e}")
#         # Log the raw response if available for debugging
#         if 'response' in locals() and hasattr(response, 'text'):
#             logging.error(f"Raw API response text: {response.text}")
#         sys.exit(1)

#     # --- Process and Log Results ---
#     results_log = []
#     for i in range(len(QUESTIONS)):
#         question_num_str = str(i + 1)
        
#         question_text = QUESTIONS[i]
#         reference_answer = REFERENCE_ANSWERS[i]
#         question_id = QUESTION_IDS[i]
        
#         # Get the answer from the parsed JSON, with error handling for missing keys
#         gemini_answer = gemini_answers_dict.get(question_num_str, "ERROR: Answer not found in API response.")
        
#         is_correct, similarity = compare_answers(gemini_answer, reference_answer)
        
#         results_log.append({
#             "Question ID": question_id,
#             "Question": question_text,
#             "Reference Answer": reference_answer,
#             "Gemini Answer": gemini_answer,
#             "Result": "Correct" if is_correct else "Incorrect",
#             "Similarity Score (%)": similarity
#         })

#     # --- Save to Excel ---
#     try:
#         logging.info(f"Saving results to '{OUTPUT_FILENAME}'...")
#         df = pd.DataFrame(results_log)
        
#         # Use ExcelWriter to allow for adding charts
#         with pd.ExcelWriter(OUTPUT_FILENAME, engine='openpyxl') as writer:
#             df.to_excel(writer, sheet_name='Evaluation Results', index=False)
            
#             # (Bonus) Add the accuracy chart
#             create_accuracy_chart(writer, 'Evaluation Results', len(QUESTIONS))
            
#         logging.info("✅ Evaluation complete. Excel report generated successfully.")

#     except Exception as e:
#         logging.error(f"Failed to save results to Excel file. Error: {e}")


# if __name__ == "__main__":
#     main()