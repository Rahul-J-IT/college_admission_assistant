"""
rag_chain.py (STABLE - NO langchain-groq dependency)
"""

# Updated imports for LangChain 1.x
from langchain_classic.chains import create_history_aware_retriever

# Prompts and Messages remain in core
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory

# Groq remains in its dedicated integration package
from langchain_groq import ChatGroq

from config import GROQ_API_KEY, GROQ_MODEL
from vectorstore import get_retriever


# ─────────────────────────────
# In-Memory Chat History
# ─────────────────────────────
class InMemoryChatHistory(BaseChatMessageHistory):
    """Simple in-memory implementation of chat message history."""
    
    def __init__(self):
        self.messages: list[BaseMessage] = []
    
    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add messages to the history."""
        self.messages.extend(messages)
    
    def clear(self) -> None:
        """Clear the message history."""
        self.messages = []


# Session history storage (keyed by session_id)
_session_history = {}


# ─────────────────────────────
# LLM (USING GROQ VIA OPENAI-COMPATIBLE API)
# ─────────────────────────────
def _build_llm():
    return ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name=GROQ_MODEL,
        temperature=0.2,
        max_tokens=2048,
    )


# ─────────────────────────────
# Memory
# ─────────────────────────────
def _get_session_history(session_id: str):
    """Get or create chat message history for a session."""
    if session_id not in _session_history:
        _session_history[session_id] = InMemoryChatHistory()
    return _session_history[session_id]


def clear_session_history(session_id: str = "default") -> None:
    """Clear the in-memory chat history for a session."""
    if session_id in _session_history:
        _session_history[session_id].clear()
        del _session_history[session_id]


# ─────────────────────────────
# Prompt
# ─────────────────────────────
CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Given a chat history and the latest user question which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
])

# Use a simple string prompt template for QA that produces string output
QA_PROMPT = PromptTemplate.from_template(
    """You are a Tamil Nadu college admissions assistant. Your role is to provide direct, helpful answers about college admissions, documents, eligibility, and related topics.

Context from database:
{context}

Previous conversation:
{chat_history}

User: {input}

CRITICAL INSTRUCTIONS:
- NEVER include any thinking, planning, or reasoning in your response
- NEVER explain what you will do or how you will respond
- NEVER use phrases like "I should", "I need to", "Let me", "I will", "First I", etc.
- ONLY provide the direct answer to the user's question
- Format with bullet points or clear structure
- Start immediately with the answer content
- If you need to think, do it silently - only output the final response

Answer:"""
)


# ─────────────────────────────
# RAG CHAIN
# ─────────────────────────────
def build_rag_chain(vectorstore):
    """Build and return components for RAG chain."""
    llm = _build_llm()
    retriever = get_retriever(vectorstore)

    # Create history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, CONDENSE_QUESTION_PROMPT
    )

    return history_aware_retriever, llm


# ─────────────────────────────
# Helper
# ─────────────────────────────
def _format_chat_history(messages: list[BaseMessage]) -> str:
    """Format message history as a readable string."""
    if not messages:
        return ""
    
    history_str = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history_str += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            history_str += f"Assistant: {msg.content}\n"
    return history_str.strip()


def ask(chain_tuple, question: str, session_id: str = "default"):
    """
    Ask a question and get an answer while maintaining conversation history.
    
    Args:
        chain_tuple: (history_aware_retriever, llm) from build_rag_chain
        question: The user's question
        session_id: Session ID for maintaining separate conversation histories
    
    Returns a dict with:
      - "answer": str - the AI response
      - "source_documents": list - documents used for context
    """
    history_aware_retriever, llm = chain_tuple
    
    # Get session history
    history = _get_session_history(session_id)
    chat_history = history.messages
    
    # Format chat history as string for the prompt
    formatted_history = _format_chat_history(chat_history)
    
    # Get relevant documents
    docs = history_aware_retriever.invoke({
        "input": question,
        "chat_history": chat_history,
    })
    
    # Format documents
    formatted_docs = "\n\n".join(doc.page_content for doc in docs)
    
    # Format the prompt with all variables
    prompt_text = QA_PROMPT.format(
        context=formatted_docs,
        chat_history=formatted_history,
        input=question,
    )
    
    # Get the LLM answer
    response = llm.invoke(prompt_text)
    answer = response.content if hasattr(response, 'content') else str(response)
    
    # Clean up the answer by removing thinking/reasoning text
    answer = _clean_answer(answer)
    
    # Add to message history
    history.add_messages([
        HumanMessage(content=question),
        AIMessage(content=answer),
    ])
    
    return {
        "answer": answer,
        "source_documents": docs,
    }


def _clean_answer(text: str) -> str:
    """
    Remove thinking/reasoning patterns from the answer.
    Aggressive cleaning to remove all internal monologue.
    """
    # First pass: remove thinking markers and explanations
    thinking_patterns = [
        'I should',
        'I need to',
        'Let me',
        'I will',
        'First, I',
        'Okay,',
        'Wait,',
        'Hmm,',
        'Based on',
        'Looking at',
        'I can see',
        'From the',
        'The context',
        'It seems',
        'I think',
        'I believe',
        'Perhaps',
        'Maybe',
        'Since the',
        'As the',
        'However,',
        'But the',
        'So the',
        'Make sure to',
        'Keep in mind',
        'Remember that',
        'Note that',
        'Find all',
        'Identify',
        'Detect',
        'Determine',
        'Start with',
        'Begin by',
        'Use bullet points',
        'Format',
        'Provide',
        'Give',
        'List',
        'Tell',
        'Include',
        'No explanations',
        'Do NOT',
        'CRITICAL INSTRUCTIONS',
        'Never include',
        'Only provide',
    ]
    
    lines = text.split('\n')
    result_lines = []
    found_content = False
    
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        
        # Skip empty lines at the beginning
        if not found_content and not stripped:
            continue
        
        # Check if this line is thinking/instruction
        is_thinking = any(pattern.lower() in lower for pattern in thinking_patterns)
        
        # If we haven't found real content yet
        if not found_content:
            # Skip if it's thinking
            if is_thinking:
                continue
            # If it's not thinking and not empty, mark as found and include it
            if stripped and not is_thinking:
                found_content = True
                result_lines.append(line)
        else:
            # After finding content, only filter out obvious meta-instructions
            if 'CRITICAL INSTRUCTIONS' in line or 'INSTRUCTIONS' in line:
                continue
            result_lines.append(line)
    
    result = '\n'.join(result_lines).strip()
    
    # Second pass: if still starts with thinking, remove that section
    if result:
        first_line_lower = result.split('\n')[0].lower()
        if any(pattern.lower() in first_line_lower for pattern in ['i should', 'i need', 'let me', 'ok,', 'wait,']):
            # Find the first line that looks like actual content
            lines = result.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not any(p.lower() in line.lower() for p in ['i should', 'i need', 'let me', 'ok,', 'wait,', 'maybe', 'perhaps', 'i think', 'i believe', 'the user', 'the question']):
                    result = '\n'.join(lines[i:]).strip()
                    break
    
    return result