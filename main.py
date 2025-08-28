#!/usr/bin/env python3
"""
RAG Chatbot - Main Entry Point
Simple startup script for the RAG chatbot application
"""

import os
import sys
from api import app

def main():
    """Main function to start the RAG chatbot server"""
    print("🤖 RAG Chatbot Starting...")
    print("�� Loading document processor...")
    print("🔍 Initializing vector database...")
    print("🧠 Connecting to language model...")
    print("✅ Server ready!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔗 Backend API: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False
    )

if __name__ == "__main__":
    main()
