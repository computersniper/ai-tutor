# 多智能体AI助教系统 - Data Structures and Algorithms

**🌐 Language:** [English](#) | [中文](readme_zh.md)

## Overview

📚 Multi-Agent AI Teaching Assistant System for Data Structures and Algorithms Course
A specialized AI teaching assistant system that simulates a team of expert TAs, each focusing on different aspects of course support. This system helps students with concept explanations, code debugging, practice generation, and review planning while maintaining academic integrity.

## Live Demos
Chinese Demo: http://8.138.234.143:5000/

English Demo: http://8.138.234.143:5001/

## Key Features
Multi-Agent Architecture: Four specialized agents working together under a central router

Intelligent Routing: Smart classification and routing of student questions

Course Context Awareness: Grounded in actual course materials and terminology

24/7 Support: Available anytime outside regular TA hours

Dual Language Support: English and Chinese interfaces

Ethical Guardrails: Prevents academic misconduct while providing helpful guidance

## System Architecture
![System Architecture](./images/system_architecture.png)

The system follows a multi-agent architecture with the following components:

Router Agent: Central coordinator that analyzes and classifies incoming questions

Concept Agent: Provides theoretical explanations and algorithm principles

Code Agent: Offers debugging assistance and code analysis

Practice Agent: Generates customized exercises and problems

Review Agent: Creates study plans and exam preparation materials

## Interface Preview
![](./images/lab_assistance.png)

## Specialized Agents
### Concept Agent - Theoretical explanations and algorithm principles

Example: "Explain how AVL trees maintain balance"

Responds with step-by-step explanations using course materials

### Code Agent - Debugging assistance and code analysis

Example: "Help debug my binary search tree implementation"

Analyzes code for logical errors, boundary issues, and performance problems

### Practice Agent - Customized exercise generation

Example: "Give me 5 medium difficulty problems on binary trees"

Generates practice problems matching course style and difficulty

### Review Agent - Study planning and exam preparation

Example: "Create a study plan for the sorting algorithms chapter"

Provides structured review guides and key point summaries

## Quick Start
### Prerequisites
Python 3.8+

DeepSeek API key

### Installation
Clone the repository:

bash
git clone https://github.com/computersniper/ai-tutor.git
cd multi-agent-ai-tutor
Install dependencies:

bash
pip install flask flask-cors python-dotenv PyPDF2 python-pptx openai
Set up environment variables:

bash
export DEEPSEEK_API_KEY="your-api-key-here"
### Running the System
Command Line Interface:

bash
python ta_agents_history.py
Web Interface:

bash
python app.py
Visit http://localhost:5000 for the web interface.

## Project Structure
text
ai-ta-assistant/
├── app.py                    # Flask web application
├── ta_agents_history.py      # Core multi-agent system
├── deepseek_client.py        # DeepSeek API wrapper
├── course_materials/         # Course knowledge base
├── images/                   # System diagrams and screenshots
│   ├── system_architecture.png
│   └── lab_assistance.png
├── pending_for_human.jsonl   # Questions needing human TA
├── conversations.json        # Conversation history
├── requirements.txt          # Python dependencies
└── README.md                 # This file
## Development Workflow Report
The project was developed in three phases:

Phase 1 - Core Multi-Agent Engine (Nov 28)

Developed Router Agent and four specialized agents

Implemented basic knowledge base system

Created functional command-line prototype

Phase 2 - Web Interface Development (Nov 29)

Built Flask-based web interface with dual-language support

Added conversation history management

Implemented improved user interface and session management

Phase 3 - Deployment and Server Setup (Dec 1)

Deployed system on cloud server (8.138.234.143)

Set up dual ports for Chinese (5000) and English (5001) interfaces

Implemented error handling, logging, and performance optimizations

## Ethical Considerations
The system includes built-in safeguards:

Automatically detects and escalates exam-related questions to human TAs

Avoids providing complete solutions to homework and lab problems

Promotes active learning through guided problem-solving

Maintains consistent answers based on official course materials

## Future Improvements
Embedding-Based Query Processing: Reduce latency with vector-based pre-classification

Enhanced Knowledge Base: Hybrid system combining global context with targeted retrieval

Multi-modal Support: Image uploads and code execution capabilities

Personalized Learning Paths: Student progress tracking and adaptive recommendations

## License
This project is open-source and available under the MIT License.