
"""
PDF Processing Service for Document Analysis
Handles PDF upload, text extraction, and AI-powered analysis
"""
import os
import logging
import PyPDF2
import tempfile
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
import re

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        """Initialize PDF processing service"""
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.pdf'}
        logger.info("✅ PDF service initialized")

    def is_valid_file(self, file: FileStorage) -> tuple[bool, str]:
        """Validate uploaded PDF file"""
        if not file or not file.filename:
            return False, "No file provided"
        
        if not file.filename.lower().endswith('.pdf'):
            return False, "Only PDF files are allowed"
        
        # Check file size (approximate)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > self.max_file_size:
            return False, f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
        
        return True, "Valid file"

    def extract_text_from_pdf(self, file: FileStorage) -> Dict[str, Any]:
        """Extract text content from PDF file"""
        try:
            # Validate file
            is_valid, message = self.is_valid_file(file)
            if not is_valid:
                return {
                    'success': False,
                    'error': message
                }

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                file.save(temp_file.name)
                
                # Extract text using PyPDF2
                text_content = ""
                page_count = 0
                
                with open(temp_file.name, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    page_count = len(pdf_reader.pages)
                    
                    for page_num, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        except Exception as e:
                            logger.warning(f"Error extracting page {page_num + 1}: {e}")
                            continue
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                # Clean and validate extracted text
                text_content = self._clean_text(text_content)
                
                if len(text_content.strip()) < 50:
                    return {
                        'success': False,
                        'error': 'Could not extract readable text from PDF'
                    }
                
                return {
                    'success': True,
                    'text': text_content,
                    'page_count': page_count,
                    'word_count': len(text_content.split()),
                    'char_count': len(text_content),
                    'filename': file.filename
                }
                
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            return {
                'success': False,
                'error': f'PDF processing failed: {str(e)}'
            }

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines that might be headers/footers
            if len(line) > 3 and not line.isdigit():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()

    def analyze_pdf_content(self, text: str, analysis_type: str = 'summarize') -> Dict[str, Any]:
        """Analyze PDF content using AI techniques"""
        try:
            if analysis_type == 'summarize':
                return self._summarize_content(text)
            elif analysis_type == 'questions':
                return self._generate_questions(text)
            elif analysis_type == 'key_points':
                return self._extract_key_points(text)
            elif analysis_type == 'concepts':
                return self._extract_concepts(text)
            else:
                return {
                    'success': False,
                    'error': f'Unknown analysis type: {analysis_type}'
                }
        except Exception as e:
            logger.error(f"PDF analysis error: {e}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }

    def _summarize_content(self, text: str) -> Dict[str, Any]:
        """Create summary of PDF content"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Extract key sentences
        key_sentences = []
        
        # First sentence
        if sentences:
            key_sentences.append(sentences[0])
        
        # Sentences with important keywords
        important_keywords = ['important', 'significant', 'key', 'main', 'conclusion', 'result', 'finding']
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in important_keywords):
                key_sentences.append(sentence)
                if len(key_sentences) >= 5:
                    break
        
        # Fill with middle sentences if needed
        if len(key_sentences) < 3 and len(sentences) > 2:
            middle_start = len(sentences) // 3
            middle_end = 2 * len(sentences) // 3
            key_sentences.extend(sentences[middle_start:middle_end][:3-len(key_sentences)])
        
        summary = '. '.join(key_sentences[:5]) + '.'
        
        return {
            'success': True,
            'summary': summary,
            'original_length': len(text.split()),
            'summary_length': len(summary.split()),
            'compression_ratio': f"{len(summary.split())}/{len(text.split())} words"
        }

    def _generate_questions(self, text: str) -> Dict[str, Any]:
        """Generate questions and answers from PDF content"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        questions = []
        
        # Generate different types of questions
        for sentence in sentences[:20]:
            # What questions
            if any(word in sentence.lower() for word in ['is', 'are', 'was', 'were', 'means', 'defined']):
                parts = re.split(r'\s+(?:is|are|was|were|means|defined as)\s+', sentence, 1)
                if len(parts) == 2:
                    questions.append({
                        'question': f"What is {parts[0].strip()}?",
                        'answer': parts[1].strip(),
                        'type': 'definition'
                    })
            
            # Why questions
            if 'because' in sentence.lower():
                parts = sentence.split('because', 1)
                if len(parts) == 2:
                    questions.append({
                        'question': f"Why {parts[0].strip().lower()}?",
                        'answer': f"Because {parts[1].strip()}",
                        'type': 'explanation'
                    })
            
            # How questions
            if any(word in sentence.lower() for word in ['process', 'method', 'procedure', 'steps']):
                questions.append({
                    'question': f"How does the process described in '{sentence[:50]}...' work?",
                    'answer': sentence,
                    'type': 'process'
                })
        
        return {
            'success': True,
            'questions': questions[:10],
            'total_generated': len(questions)
        }

    def _extract_key_points(self, text: str) -> Dict[str, Any]:
        """Extract key points from PDF content"""
        sentences = re.split(r'[.!?]+', text)
        key_points = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:
                # Look for numbered points
                if re.match(r'^\d+\.', sentence):
                    key_points.append(sentence)
                # Look for bullet points
                elif sentence.startswith(('•', '-', '*')):
                    key_points.append(sentence)
                # Look for important keywords
                elif any(keyword in sentence.lower() for keyword in [
                    'important', 'key', 'main', 'significant', 'crucial', 'essential',
                    'first', 'second', 'third', 'finally', 'conclusion'
                ]):
                    key_points.append(sentence)
        
        return {
            'success': True,
            'key_points': key_points[:15],
            'total_found': len(key_points)
        }

    def _extract_concepts(self, text: str) -> Dict[str, Any]:
        """Extract key concepts from PDF content"""
        # Find capitalized terms (potential concepts)
        concepts = []
        
        # Look for capitalized terms
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Look for terms in quotes
        quoted_terms = re.findall(r'"([^"]*)"', text)
        
        # Look for terms in parentheses
        parenthetical_terms = re.findall(r'\(([^)]*)\)', text)
        
        all_terms = capitalized_terms + quoted_terms + parenthetical_terms
        
        # Filter and deduplicate
        seen = set()
        for term in all_terms:
            if len(term) > 2 and len(term) < 50 and term not in seen:
                concepts.append({
                    'term': term,
                    'context': self._find_context(text, term)
                })
                seen.add(term)
        
        return {
            'success': True,
            'concepts': concepts[:20],
            'total_found': len(concepts)
        }

    def _find_context(self, text: str, term: str) -> str:
        """Find context around a term"""
        sentences = text.split('.')
        for sentence in sentences:
            if term.lower() in sentence.lower():
                return sentence.strip()[:200] + '...' if len(sentence) > 200 else sentence.strip()
        return ""

    def extract_text_from_file(self, file: FileStorage) -> Dict[str, Any]:
        """Extract text from uploaded file (PDF, DOC, DOCX, TXT)"""
        try:
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                return self.extract_text_from_pdf(file)
            elif filename.endswith('.txt'):
                content = file.read().decode('utf-8')
                return {
                    'success': True,
                    'text': content,
                    'filename': file.filename,
                    'word_count': len(content.split()),
                    'char_count': len(content)
                }
            elif filename.endswith(('.doc', '.docx')):
                # For DOC/DOCX files, we'll use python-docx
                try:
                    from docx import Document
                    doc = Document(file)
                    text_content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                    
                    return {
                        'success': True,
                        'text': text_content,
                        'filename': file.filename,
                        'word_count': len(text_content.split()),
                        'char_count': len(text_content)
                    }
                except ImportError:
                    return {
                        'success': False,
                        'error': 'python-docx library not available for DOC/DOCX files'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Unsupported file format'
                }
        except Exception as e:
            logger.error(f"File text extraction error: {e}")
            return {
                'success': False,
                'error': f'File processing failed: {str(e)}'
            }

    def format_pdf_analysis_response(self, analysis_data: Dict[str, Any], analysis_type: str, persona: str = 'default') -> str:
        """Format PDF analysis results into natural language response"""
        if not analysis_data['success']:
            if persona == 'pirate':
                return f"Arrr! {analysis_data['error']} The document seas be treacherous, matey!"
            else:
                return f"I'm sorry, {analysis_data['error']}"

        if persona == 'pirate':
            if analysis_type == 'summarize':
                response = f"Ahoy! I've sailed through yer document and here be the treasure summary:\n\n"
                response += f"📜 {analysis_data['summary']}\n\n"
                response += f"⚓ Condensed from {analysis_data['compression_ratio']} - much easier to digest, me hearty!"
                
            elif analysis_type == 'questions':
                response = f"Shiver me timbers! I've created some study questions for ye:\n\n"
                for i, q in enumerate(analysis_data['questions'][:5], 1):
                    response += f"{i}. Q: {q['question']}\n   A: {q['answer']}\n\n"
                response += f"That be {analysis_data['total_generated']} questions to test yer knowledge!"
                
            elif analysis_type == 'key_points':
                response = f"Arrr! Here be the key treasures I found in yer document:\n\n"
                for i, point in enumerate(analysis_data['key_points'][:10], 1):
                    response += f"{i}. {point}\n"
                response += f"\n⚓ Found {analysis_data['total_found']} important points total!"
                
            elif analysis_type == 'concepts':
                response = f"Avast! Here be the important concepts from yer document:\n\n"
                for i, concept in enumerate(analysis_data['concepts'][:8], 1):
                    response += f"{i}. **{concept['term']}**: {concept['context'][:100]}...\n\n"
                response += f"Found {analysis_data['total_found']} concepts to master!"
                
        else:
            if analysis_type == 'summarize':
                response = f"Document Summary:\n\n"
                response += f"📄 {analysis_data['summary']}\n\n"
                response += f"📊 Condensed from {analysis_data['compression_ratio']} for easier reading!"
                
            elif analysis_type == 'questions':
                response = f"Generated Questions & Answers:\n\n"
                for i, q in enumerate(analysis_data['questions'][:5], 1):
                    response += f"{i}. Q: {q['question']}\n   A: {q['answer']}\n\n"
                response += f"Total generated: {analysis_data['total_generated']} questions"
                
            elif analysis_type == 'key_points':
                response = f"Key Points Extracted:\n\n"
                for i, point in enumerate(analysis_data['key_points'][:10], 1):
                    response += f"{i}. {point}\n"
                response += f"\nTotal found: {analysis_data['total_found']} important points"
                
            elif analysis_type == 'concepts':
                response = f"Key Concepts Identified:\n\n"
                for i, concept in enumerate(analysis_data['concepts'][:8], 1):
                    response += f"{i}. **{concept['term']}**: {concept['context'][:100]}...\n\n"
                response += f"Total found: {analysis_data['total_found']} concepts"

        response += "\n\nWould you like me to analyze the document differently or focus on specific sections?"
        return response
