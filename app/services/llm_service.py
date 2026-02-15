import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
import io

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")

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

    def generate_personalized_questions(self, resume_text: str, num_questions: int = 3) -> list[str]:
        if not resume_text:
            return ["Could not read resume. Please tell us about your background."]

        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert career coach and onboarding specialist.
            Based on the following resume content, generate {num} highly personalized 
            questions to ask the candidate to better understand their specific skills, 
            projects, or gaps in their experience.
            
            Resume Content:
            {resume_text}
            
            Return ONLY the questions, one per line. Do not number them.
            """
        )
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"resume_text": resume_text, "num": num_questions})
            # content is likely a string with newlines
            questions = [q.strip() for q in response.content.split('\n') if q.strip()]
            return questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            return ["Tell us more about your recent project.", "What are your career goals?", "Why do you want to join us?"]
