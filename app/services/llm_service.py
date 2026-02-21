import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
import io
import json

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini")

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            pdf_stream = io.BytesIO(file_content)
            reader = PdfReader(pdf_stream)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    def analyze_resume_and_generate_questions(self, resume_text: str, num_questions: int = 4) -> dict:
        """
        Analyzes the student's resume with the lens of a higher-education advisor.
        Returns a dict with:
          - analysis: a brief profile summary
          - questions: a list of personalized higher-ed focused questions
        """
        if not resume_text:
            return {
                "analysis": "Could not read the resume. Please check the PDF format.",
                "questions": [
                    "What field of study are you interested in pursuing for higher education?",
                    "What are your target countries or regions for university applications?",
                    "Do you have a preference for program type (Masters, PhD, MBA, etc.)?",
                    "What is your current GPA or academic standing?"
                ]
            }

        prompt = ChatPromptTemplate.from_template(
            """
            You are PathPilot, an AI-powered higher education guidance advisor.
            A student has uploaded their resume/CV and is seeking help finding the right 
            university and graduate program for them.

            Your job is to:
            1. Briefly analyze their academic and professional background (2-3 sentences).
            2. Generate {num} highly personalized questions to gather information you need 
               to recommend the best universities and programs for them.

            Focus your questions on:
            - Their target field/discipline for higher education (e.g. Computer Science, MBA, Law)
            - Target countries or regions (e.g. USA, Canada, UK, Europe)
            - Type of program (Masters, PhD, MBA, Diploma, etc.)
            - Their academic goals (research, industry, academia, entrepreneurship)
            - Any specific preferences (funding, rankings, campus life, specializations)
            - Gaps or strengths in their profile that universities consider (GPA, work experience, publications, etc.)

            Do NOT ask job-interview questions. This is ONLY about graduate/higher education search.

            Resume/CV Content:
            {resume_text}

            Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
            {{
                "analysis": "A brief 2-3 sentence summary of the student's profile and their higher education readiness.",
                "questions": [
                    "Question 1",
                    "Question 2",
                    "Question 3",
                    "Question 4"
                ]
            }}
            """
        )

        chain = prompt | self.llm

        try:
            response = chain.invoke({"resume_text": resume_text, "num": num_questions})
            content = response.content.strip()

            # Parse JSON response
            data = json.loads(content)
            return {
                "analysis": data.get("analysis", ""),
                "questions": data.get("questions", [])
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM JSON response: {e}")
            print(f"Raw response: {response.content}")
            # Fallback: try to extract questions from plain text
            return {
                "analysis": "We reviewed your resume and have a few questions to better guide you.",
                "questions": [
                    "What field or discipline are you hoping to pursue in graduate school?",
                    "Which countries or regions are you targeting for your studies?",
                    "Are you interested in a Masters, PhD, or another type of program?",
                    "Are you looking for funded programs or open to self-funded options?"
                ]
            }
        except Exception as e:
            print(f"Error generating analysis and questions: {e}")
            return {
                "analysis": "We could not fully analyze your resume at this time.",
                "questions": [
                    "What field or discipline are you hoping to pursue in graduate school?",
                    "Which countries or regions are you targeting for your studies?",
                    "Are you interested in a Masters, PhD, or another type of program?",
                    "Are you looking for funded programs or open to self-funded options?"
                ]
            }
