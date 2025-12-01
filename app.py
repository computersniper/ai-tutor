from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# File to store conversation history
CONVERSATIONS_FILE = 'conversations.json'

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_api_key")

# Attempt to initialize TA Agent system
try:
    from ta_agents_history import TeachingAssistant
    # Check if API key exists
    api_key = DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
    
    print(f"🔑 API Key Length: {len(api_key)}")
    print("🔄 Initializing TA Agent...")
    
    ta_system = TeachingAssistant(materials_folder="course_materials", session_id="web_session")
    TA_AGENT_AVAILABLE = True
    print("✅ TA Agent system initialized successfully")
except Exception as e:
    print(f"❌ TA Agent system initialization failed: {e}")
    TA_AGENT_AVAILABLE = False
    ta_system = None

# Initialize conversation history
def init_conversations():
    if not os.path.exists(CONVERSATIONS_FILE):
        initial_conversations = {
            'current': {
                'title': 'Current Conversation',
                'messages': []
            }
        }
        with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(initial_conversations, f, ensure_ascii=False, indent=2)

# Load conversation history
def load_conversations():
    if not os.path.exists(CONVERSATIONS_FILE):
        init_conversations()
    with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# Save conversation history
def save_conversations(conversations):
    with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

# Get AI response using TA Agent
def get_ai_response_ta_agent(message, conversation_id="current"):
    """Generate AI response using TA Agent system"""
    if not TA_AGENT_AVAILABLE or ta_system is None:
        print("⚠️ Using fallback response system")
        return get_ai_response_fallback(message)
    
    try:
        print(f"🤖 Processing message with TA Agent: {message[:50]}...")
        
        # Create separate TA instance for each conversation to maintain context
        session_id = f"web_{conversation_id}"
        ta = TeachingAssistant(materials_folder="course_materials", session_id=session_id)
        
        # Process user message
        result = ta.handle_question(message)
        print(f"📊 Router decision: {result['router']}")
        
        if result.get('ai_answer'):
            return result['ai_answer']
        else:
            return f"{result.get('message', 'AI Teaching Assistant is thinking...')}"
    
    except Exception as e:
        print(f"❌ TA Agent processing error: {e}")
        import traceback
        traceback.print_exc()
        return get_ai_response_fallback(message)

# Fallback response function
def get_ai_response_fallback(message):
    """Fallback response when TA Agent is unavailable"""
    return f"I am the AI Teaching Assistant for Data Structures and Algorithms. You asked: {message}\n\nThe TA Agent system is currently initializing, please try again later."

# API endpoints
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    conversations = load_conversations()
    return jsonify(conversations)

@app.route('/api/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    """Get specific conversation"""
    conversations = load_conversations()
    if conv_id in conversations:
        return jsonify(conversations[conv_id])
    else:
        return jsonify({'error': 'Conversation not found'}), 404

@app.route('/api/conversations/<conv_id>/messages', methods=['POST'])
def add_message(conv_id):
    """Add message to conversation"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Message content is required'}), 400
    
    conversations = load_conversations()
    if conv_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    user_message_content = data['content']
    print(f"👤 User message: {user_message_content}")
    
    # Add user message
    user_message = {
        'sender': 'user',
        'content': user_message_content
    }
    conversations[conv_id]['messages'].append(user_message)
    
    # Update conversation title (if it's a new conversation)
    if conversations[conv_id]['title'] in ['New Conversation', 'Current Conversation'] and user_message_content:
        conversations[conv_id]['title'] = user_message_content[:20] + '...' if len(user_message_content) > 20 else user_message_content
    
    # Generate AI response - using TA Agent system
    print("🔄 Generating AI response...")
    ai_response_content = get_ai_response_ta_agent(user_message_content, conv_id)
    print(f"🤖 AI Response: {ai_response_content[:100]}...")
    
    ai_response = {
        'sender': 'ai',
        'content': ai_response_content
    }
    conversations[conv_id]['messages'].append(ai_response)
    
    # Save conversation
    save_conversations(conversations)
    
    return jsonify({
        'user_message': user_message,
        'ai_response': ai_response
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy', 
        'ta_agent': 'available' if TA_AGENT_AVAILABLE else 'unavailable'
    })

@app.route('/')
def index():
    """Serve frontend page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Teaching Assistant</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <!-- Include Font Awesome icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: #f8fafc;
                height: 100vh;
                overflow: hidden;
            }
            
            .app-container {
                display: flex;
                height: 100vh;
            }
            
            /* Left Sidebar - History */
            .left-sidebar {
                width: 280px;
                background: white;
                border-right: 1px solid #e1e5e9;
                display: flex;
                flex-direction: column;
            }
            
            .sidebar-header {
                padding: 20px;
                border-bottom: 1px solid #e1e5e9;
            }
            
            .sidebar-header h2 {
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .new-chat-btn {
                width: 100%;
                padding: 12px 16px;
                background: #1e40af;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                margin-top: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            
            .new-chat-btn:hover {
                background: #1e3a8a;
            }
            
            .history-list {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
            }
            
            .history-item {
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: pointer;
                border: 1px solid transparent;
                font-size: 14px;
                color: #64748b;
            }
            
            .history-item:hover {
                background: #f1f5f9;
            }
            
            .history-item.active {
                background: #eff6ff;
                border-color: #1e40af;
                color: #1e40af;
                font-weight: 500;
            }
            
            .empty-history {
                text-align: center;
                color: #94a3b8;
                font-size: 14px;
                padding: 40px 20px;
            }
            
            /* Middle Chat Area */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: white;
            }
            
            .chat-header {
                background: white;
                padding: 16px 24px;
                border-bottom: 1px solid #e1e5e9;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .chat-header h1 {
                font-size: 20px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .status-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #22c55e;
            }
            
            .status-dot.offline {
                background: #ef4444;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 24px;
                background: #f8fafc;
            }
            
            .message {
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }
            
            .user-message {
                flex-direction: row-reverse;
            }
            
            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
                flex-shrink: 0;
            }
            
            .user-avatar {
                background: #1e40af;
                color: white;
            }
            
            .ai-avatar {
                background: #64748b;
                color: white;
            }
            
            .message-bubble {
                max-width: 70%;
                padding: 16px 20px;
                border-radius: 18px;
                line-height: 1.5;
            }
            
            .user-bubble {
                background: #1e40af;
                color: white;
                border-bottom-right-radius: 4px;
            }
            
            .ai-bubble {
                background: white;
                color: #334155;
                border: 1px solid #e2e8f0;
                border-bottom-left-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .input-area {
                padding: 20px 24px;
                background: white;
                border-top: 1px solid #e1e5e9;
            }
            
            .input-container {
                display: flex;
                gap: 12px;
                align-items: flex-end;
            }
            
            #messageInput {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                font-size: 14px;
                resize: none;
                min-height: 44px;
                max-height: 120px;
                font-family: inherit;
            }
            
            #messageInput:focus {
                outline: none;
                border-color: #1e40af;
                box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
            }
            
            #sendBtn {
                padding: 12px 20px;
                background: #1e40af;
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                flex-shrink: 0;
                height: 44px;
            }
            
            #sendBtn:hover {
                background: #1e3a8a;
            }
            
            #sendBtn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
            }
            
            /* Right Sidebar - Learning Resources */
            .right-sidebar {
                width: 320px;
                background: white;
                border-left: 1px solid #e1e5e9;
                display: flex;
                flex-direction: column;
                overflow-y: auto;
            }
            
            .resource-header {
                padding: 20px;
                border-bottom: 1px solid #e1e5e9;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .resource-header h3 {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .resource-content {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
            }
            
            .resource-section {
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 1rem;
                margin-bottom: 1rem;
            }
            
            .resource-section:last-child {
                border-bottom: none;
            }
            
            .resource-section h4 {
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 12px;
            }
            
            .resource-section .space-y-2 > * + * {
                margin-top: 8px;
            }
            
            .resource-section .space-y-3 > * + * {
                margin-top: 12px;
            }
            
            .text-sm {
                font-size: 14px;
            }
            
            .text-base {
                font-size: 16px;
            }
            
            .text-gray-700 {
                color: #374151;
            }
            
            .text-gray-600 {
                color: #6b7280;
            }
            
            .text-gray-800 {
                color: #1f2937;
            }
            
            .text-red-500 {
                color: #ef4444;
            }
            
            .text-orange-500 {
                color: #f59e0b;
            }
            
            .font-medium {
                font-weight: 500;
            }
            
            .font-semibold {
                font-weight: 600;
            }
            
            .ddl-card {
                border: 1px solid #f1f5f9;
                border-radius: 8px;
                padding: 12px;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                border-left: 3px solid #ef4444;
            }
            
            .ddl-card.warning {
                border-left: 3px solid #f59e0b;
            }
            
            .resource-link {
                display: flex;
                align-items: center;
                padding: 0.5rem 0;
                color: #1e40af;
                text-decoration: none;
                transition: all 0.2s ease;
            }
            
            .resource-link:hover {
                color: #1e3a8a;
                padding-left: 0.25rem;
            }
            
            .thinking {
                display: flex;
                align-items: center;
                color: #64748b;
                font-style: italic;
            }
            
            .typing-dots {
                display: flex;
                margin-left: 8px;
            }
            
            .typing-dot {
                width: 4px;
                height: 4px;
                border-radius: 50%;
                background-color: #64748b;
                margin: 0 2px;
                animation: typing 1.4s infinite ease-in-out;
            }
            
            .typing-dot:nth-child(1) { animation-delay: -0.32s; }
            .typing-dot:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typing {
                0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                40% { transform: scale(1); opacity: 1; }
            }
            
            /* Markdown Content Styles */
            .markdown-content {
                line-height: 1.6;
            }
            
            .markdown-content h1, 
            .markdown-content h2, 
            .markdown-content h3 {
                margin-top: 16px;
                margin-bottom: 8px;
                color: #1e40af;
            }
            
            .markdown-content h1 {
                font-size: 1.3em;
                border-bottom: 1px solid #e1e5e9;
                padding-bottom: 6px;
            }
            
            .markdown-content h2 {
                font-size: 1.1em;
            }
            
            .markdown-content h3 {
                font-size: 1em;
            }
            
            .markdown-content p {
                margin: 8px 0;
            }
            
            .markdown-content ul, 
            .markdown-content ol {
                margin: 8px 0;
                padding-left: 20px;
            }
            
            .markdown-content li {
                margin: 4px 0;
            }
            
            .markdown-content code {
                background-color: #f1f5f9;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.9em;
                color: #dc2626;
            }
            
            .markdown-content pre {
                background-color: #1e293b;
                color: #e2e8f0;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                margin: 12px 0;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            .markdown-content pre code {
                background: none;
                padding: 0;
                color: inherit;
            }
            
            .markdown-content blockquote {
                border-left: 4px solid #cbd5e1;
                padding-left: 16px;
                margin: 12px 0;
                color: #64748b;
                font-style: italic;
            }
            
            .markdown-content table {
                border-collapse: collapse;
                width: 100%;
                margin: 12px 0;
                font-size: 0.9em;
            }
            
            .markdown-content th, 
            .markdown-content td {
                border: 1px solid #cbd5e1;
                padding: 6px 8px;
                text-align: left;
            }
            
            .markdown-content th {
                background-color: #f1f5f9;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Left Sidebar: History -->
            <div class="left-sidebar">
                <div class="sidebar-header">
                    <h2>AI Teaching Assistant</h2>
                    <button class="new-chat-btn">
                        <i class="fas fa-plus"></i>
                        New Conversation
                    </button>
                </div>
                <div class="history-list">
                    <div class="empty-history">
                        <i class="fas fa-comments" style="font-size: 24px; margin-bottom: 8px;"></i>
                        <p>No conversation history</p>
                        <p style="font-size: 12px; margin-top: 4px;">Start a new conversation</p>
                    </div>
                </div>
            </div>
            
            <!-- Middle Chat Area -->
            <div class="main-content">
                <div class="chat-header">
                    <h1>Data Structures & Algorithms AI Assistant</h1>
                    <div class="status-indicator">
                        <div class="status-dot" id="statusDot"></div>
                        <span id="statusText">System Status: Checking...</span>
                    </div>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai-message">
                        <div class="message-avatar ai-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-bubble ai-bubble">
                            <div class="markdown-content">
                                Hello! I'm the AI Teaching Assistant for the Data Structures and Algorithms course. I can help you with course-related questions. How can I assist you today?
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="input-area">
                    <div class="input-container">
                        <textarea id="messageInput" placeholder="Enter your question..." rows="1"></textarea>
                        <button id="sendBtn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Right Sidebar: Learning Resources -->
            <div class="right-sidebar">
                <div class="resource-header">
                    <h3>Learning Resources</h3>
                </div>
                
                <div class="resource-content">
                    <!-- Key Concepts -->
                    <div class="resource-section">
                        <h4>Key Concepts</h4>
                        <div class="space-y-2">
                            <div class="text-sm text-gray-700">• Time and Space Complexity Analysis</div>
                            <div class="text-sm text-gray-700">• Array, Linked List, Stack, Queue Operations</div>
                            <div class="text-sm text-gray-700">• Tree Traversal Methods (Preorder, Inorder, Postorder)</div>
                            <div class="text-sm text-gray-700">• Sorting Algorithms (Quick Sort, Merge Sort, Heap Sort)</div>
                            <div class="text-sm text-gray-700">• Graph Traversal (BFS, DFS)</div>
                        </div>
                    </div>
                    
                    <!-- Assignments & Deadlines -->
                    <div class="resource-section">
                        <h4>Assignments & Deadlines</h4>
                        <div class="space-y-3">
                            <div class="ddl-card">
                                <div class="text-base font-medium text-gray-800">Assignment 1: Arrays & Linked Lists</div>
                                <div class="text-sm text-gray-600 mt-1">Complete Chapter 3 exercises</div>
                                <div class="flex justify-between items-center mt-2">
                                    <div class="text-sm font-medium text-red-500">Due: Nov 30</div>
                                    <div class="text-sm text-gray-500">3 days left</div>
                                </div>
                            </div>
                            
                            <div class="ddl-card warning">
                                <div class="text-base font-medium text-gray-800">Assignment 2: Stacks & Queues</div>
                                <div class="text-sm text-gray-600 mt-1">Implement basic stack and queue operations</div>
                                <div class="flex justify-between items-center mt-2">
                                    <div class="text-sm font-medium text-orange-500">Due: Dec 7</div>
                                    <div class="text-sm text-gray-500">10 days left</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recommended Learning Resources -->
                    <div class="resource-section">
                        <h4>Recommended Learning Resources</h4>
                        <div class="space-y-2">
                            <a href="https://leetcode.com" target="_blank" class="resource-link">
                                <i class="fas fa-external-link-alt mr-3 text-sm"></i>
                                <span class="text-sm">LeetCode Algorithm Practice</span>
                            </a>
                            <a href="https://www.geeksforgeeks.org" target="_blank" class="resource-link">
                                <i class="fas fa-external-link-alt mr-3 text-sm"></i>
                                <span class="text-sm">GeeksforGeeks</span>
                            </a>
                            <a href="https://www.cs.usfca.edu/~galles/visualization/Algorithms.html" target="_blank" class="resource-link">
                                <i class="fas fa-external-link-alt mr-3 text-sm"></i>
                                <span class="text-sm">Algorithm Visualization Tool</span>
                            </a>
                            <a href="#" class="resource-link">
                                <i class="fas fa-file-alt mr-3 text-sm"></i>
                                <span class="text-sm">Course Online Notes</span>
                            </a>
                        </div>
                    </div>
                    
                    <!-- School Links & Course Homepage -->
                    <div class="resource-section">
                        <h4>School Links & Course Homepage</h4>
                        <div class="space-y-2">
                            <a href="https://www.school.edu.cn" target="_blank" class="resource-link">
                                <i class="fas fa-university mr-3 text-sm"></i>
                                <span class="text-sm">School Website</span>
                            </a>
                            <a href="https://course.school.edu.cn/dsa" target="_blank" class="resource-link">
                                <i class="fas fa-book mr-3 text-sm"></i>
                                <span class="text-sm">Course Homepage</span>
                            </a>
                            <a href="https://learning.school.edu.cn" target="_blank" class="resource-link">
                                <i class="fas fa-graduation-cap mr-3 text-sm"></i>
                                <span class="text-sm">Learning Platform</span>
                            </a>
                            <a href="https://discord.gg/school" target="_blank" class="resource-link">
                                <i class="fas fa-comments mr-3 text-sm"></i>
                                <span class="text-sm">Course Forum</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Include Markdown rendering library -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/dompurify@2.3.3/dist/purify.min.js"></script>
        <script>
            // Simple debug function
            function debug(msg) {
                console.log('[DEBUG] ' + msg);
            }
            
            // Get DOM elements
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const statusText = document.getElementById('statusText');
            const statusDot = document.getElementById('statusDot');
            
            // Configure marked options
            marked.setOptions({
                highlight: function(code, lang) {
                    return code;
                },
                breaks: true,
                gfm: true
            });

            // Render Markdown to safe HTML
            function renderMarkdown(markdownText) {
                try {
                    const rawHtml = marked.parse(markdownText);
                    const cleanHtml = DOMPurify.sanitize(rawHtml);
                    return cleanHtml;
                } catch (error) {
                    debug('Markdown rendering error: ' + error);
                    return markdownText;
                }
            }

            // Status variables
            let isThinking = false;
            
            // Check system status
            function checkSystemStatus() {
                fetch('/api/health')
                    .then(response => response.json())
                    .then(data => {
                        if (data.ta_agent === 'available') {
                            statusText.textContent = 'System Status: Normal (TA Agent available)';
                            statusDot.style.background = '#22c55e';
                        } else {
                            statusText.textContent = 'System Status: Normal (Using backup mode)';
                            statusDot.style.background = '#f59e0b';
                        }
                    })
                    .catch(error => {
                        statusText.textContent = 'System Status: Connection failed';
                        statusDot.style.background = '#ef4444';
                        statusDot.classList.add('offline');
                        debug('Failed to check system status: ' + error);
                    });
            }
            
            // Send message
            function sendMessage() {
                debug('sendMessage function called');
                
                const message = messageInput.value.trim();
                if (!message) {
                    debug('Message is empty, not sending');
                    return;
                }
                
                if (isThinking) {
                    debug('Currently thinking, not sending new message');
                    return;
                }
                
                debug('Preparing to send message: ' + message);
                
                // Add user message
                addMessage(message, 'user');
                
                // Clear input field
                messageInput.value = '';
                adjustTextareaHeight();
                
                // Disable send button
                sendBtn.disabled = true;
                
                // Show thinking state
                showThinking();
                
                // Send to backend
                fetch('/api/conversations/current/messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ content: message })
                })
                .then(response => {
                    debug('Received response, status: ' + response.status);
                    if (!response.ok) {
                        throw new Error('HTTP error: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    debug('Successfully obtained AI response');
                    removeThinking();
                    addMessage(data.ai_response.content, 'ai');
                })
                .catch(error => {
                    debug('Failed to send message: ' + error);
                    removeThinking();
                    addMessage('Sorry, failed to send message: ' + error.message, 'ai');
                })
                .finally(() => {
                    // Re-enable send button
                    sendBtn.disabled = false;
                });
            }
            
            // Add message to chat area
            function addMessage(message, sender) {
                debug('Adding message: ' + sender + ' - ' + message.substring(0, 50));
                
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (sender === 'user' ? 'user-message' : 'ai-message');
                
                // Create avatar
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar ' + (sender === 'user' ? 'user-avatar' : 'ai-avatar');
                if (sender === 'user') {
                    avatar.innerHTML = '<i class="fas fa-user"></i>';
                } else {
                    avatar.innerHTML = '<i class="fas fa-robot"></i>';
                }
                
                // Create message bubble
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble ' + (sender === 'user' ? 'user-bubble' : 'ai-bubble');
                
                if (sender === 'ai') {
                    // AI message: render Markdown
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'markdown-content';
                    contentDiv.innerHTML = renderMarkdown(message);
                    bubble.appendChild(contentDiv);
                } else {
                    // User message: display text directly
                    bubble.textContent = message;
                }
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
                chatMessages.appendChild(messageDiv);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Show thinking state
            function showThinking() {
                debug('Showing thinking state');
                isThinking = true;
                
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ai-message';
                messageDiv.id = 'thinkingIndicator';
                
                const avatar = document.createElement('div');
                avatar.className = 'message-avatar ai-avatar';
                avatar.innerHTML = '<i class="fas fa-robot"></i>';
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble ai-bubble thinking';
                bubble.innerHTML = 'Thinking<span class="typing-dots"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span></span>';
                
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
                chatMessages.appendChild(messageDiv);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Remove thinking state
            function removeThinking() {
                debug('Removing thinking state');
                isThinking = false;
                
                const thinkingIndicator = document.getElementById('thinkingIndicator');
                if (thinkingIndicator) {
                    thinkingIndicator.remove();
                }
            }
            
            // Adjust textarea height
            function adjustTextareaHeight() {
                messageInput.style.height = 'auto';
                messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
            }
            
            // Bind events
            function setupEventListeners() {
                debug('Setting up event listeners');
                
                // Send button click event
                sendBtn.addEventListener('click', function() {
                    debug('Send button clicked');
                    sendMessage();
                });
                
                // Input field enter event (Ctrl+Enter or Cmd+Enter to send)
                messageInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        debug('Enter key pressed');
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                // Textarea auto-adjust height
                messageInput.addEventListener('input', adjustTextareaHeight);
                
                // New conversation button
                document.querySelector('.new-chat-btn').addEventListener('click', function() {
                    if (confirm('Are you sure you want to start a new conversation? The current conversation will be saved to history.')) {
                        // Add logic to start new conversation here
                        chatMessages.innerHTML = `
                            <div class="message ai-message">
                                <div class="message-avatar ai-avatar">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="message-bubble ai-bubble">
                                    <div class="markdown-content">
                                        Hello! I'm the AI Teaching Assistant for the Data Structures and Algorithms course. I can help you with course-related questions. How can I assist you today?
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                });
            }
            
            // Initialize
            function init() {
                debug('Initializing application');
                setupEventListeners();
                checkSystemStatus();
                messageInput.focus();
                debug('Initialization complete');
            }
            
            // Initialize when page loads
            document.addEventListener('DOMContentLoaded', init);
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    init_conversations()
    print("=" * 60)
    print("🚀 AI Teaching Assistant System Starting...")
    print("📚 Access URL: http://localhost:5000")
    print("🤖 TA Agent Status:", "Available" if TA_AGENT_AVAILABLE else "Unavailable")
    print("🔑 API Key:", "Set" if DEEPSEEK_API_KEY else "Not Set")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)